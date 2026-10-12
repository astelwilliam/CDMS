from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.models.association_tables import department_administrator_departments
from app.models.college import College
from app.models.department import Department
from app.models.department_administrator import DepartmentAdministrator
from app.models.role import Role
from app.models.user import User
from app.repositories.department_administrator_repository import (
    DepartmentAdministratorRepository,
)
from app.services.privileged_administrator_mutation import (
    DepartmentMutationTargetNotFound,
    PrivilegedAdministratorMutationDenied,
    stage_administrator_identity_change,
    stage_department_assignment,
    stage_department_assignment_revocation,
)


@pytest.fixture
def mutation_data():
    import app.models  # noqa: F401 - register complete relationship metadata
    from app.db.session import Base

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        role = Role(name="privileged-admin-role")
        college = College(name="Privileged Admin College")
        other_college = College(name="Other Privileged Admin College")
        users = {
            "actor": User(
                email="privileged-actor@example.com",
                hashed_password="unused",
                role="super_admin",
                is_active=True,
            ),
            "linked": User(
                email="linked-mutation@example.com",
                hashed_password="unused",
                role="department_admin",
                is_active=True,
            ),
            "candidate": User(
                email="candidate-mutation@example.com",
                hashed_password="unused",
                role="department_admin",
                is_active=True,
            ),
            "inactive": User(
                email="inactive-mutation@example.com",
                hashed_password="unused",
                role="department_admin",
                is_active=False,
            ),
            "wrong_role": User(
                email="wrong-role-mutation@example.com",
                hashed_password="unused",
                role="super_admin",
                is_active=True,
            ),
        }
        db.add_all([role, college, other_college, *users.values()])
        db.flush()
        departments = {
            "first": Department(name="First", college_id=college.id),
            "second": Department(name="Second", college_id=college.id),
            "other": Department(name="Other", college_id=other_college.id),
            "deleted": Department(
                name="Deleted",
                college_id=college.id,
                deleted_at=datetime.now(timezone.utc),
            ),
        }
        db.add_all(departments.values())
        db.flush()
        administrators = {
            "linked": DepartmentAdministrator(
                name="Linked",
                email="linked-administrator@example.com",
                role_id=role.id,
                user_id=users["linked"].id,
            ),
            "unlinked": DepartmentAdministrator(
                name="Unlinked",
                email="unlinked-administrator@example.com",
                role_id=role.id,
                user_id=None,
            ),
        }
        db.add_all(administrators.values())
        db.flush()
        db.execute(
            department_administrator_departments.insert(),
            {
                "department_administrator_id": administrators["linked"].id,
                "department_id": departments["first"].id,
            },
        )
        db.commit()
        ids = {
            "users": {name: value.id for name, value in users.items()},
            "administrators": {
                name: value.id for name, value in administrators.items()
            },
            "departments": {name: value.id for name, value in departments.items()},
        }

    yield engine, ids
    engine.dispose()


def assignment_exists(db, administrator_id, department_id):
    return db.scalar(
        select(department_administrator_departments.c.department_id).where(
            department_administrator_departments.c.department_administrator_id
            == administrator_id,
            department_administrator_departments.c.department_id == department_id,
        )
    ) is not None


def test_assignment_creation_is_staged_and_rollback_safe(mutation_data):
    engine, ids = mutation_data
    with Session(engine) as db:
        assert stage_department_assignment(
            db,
            ids["users"]["actor"],
            ids["administrators"]["linked"],
            ids["departments"]["second"],
        )
        assert assignment_exists(
            db,
            ids["administrators"]["linked"],
            ids["departments"]["second"],
        )
        db.rollback()

    with Session(engine) as db:
        assert not assignment_exists(
            db,
            ids["administrators"]["linked"],
            ids["departments"]["second"],
        )


def test_assignment_revocation_is_staged_and_rollback_safe(mutation_data):
    engine, ids = mutation_data
    with Session(engine) as db:
        assert stage_department_assignment_revocation(
            db,
            ids["users"]["actor"],
            ids["administrators"]["linked"],
            ids["departments"]["first"],
        )
        assert not assignment_exists(
            db,
            ids["administrators"]["linked"],
            ids["departments"]["first"],
        )
        db.rollback()

    with Session(engine) as db:
        assert assignment_exists(
            db,
            ids["administrators"]["linked"],
            ids["departments"]["first"],
        )


def test_assignment_locks_follow_documented_table_order(mutation_data):
    engine, ids = mutation_data
    lock_tables = []

    with Session(engine) as db:
        def record_lock(execute_state):
            statement = execute_state.statement
            if getattr(statement, "_for_update_arg", None) is None:
                return
            sql = " ".join(statement.compile().string.lower().split())
            for table_name, label in (
                ("users", "users"),
                ("department_administrators", "administrators"),
                ("departments", "departments"),
                ("department_administrator_departments", "assignments"),
            ):
                if f" from {table_name} " in f" {sql} ":
                    lock_tables.append(label)
                    break

        event.listen(db, "do_orm_execute", record_lock)
        try:
            stage_department_assignment(
                db,
                ids["users"]["actor"],
                ids["administrators"]["linked"],
                ids["departments"]["second"],
            )
        finally:
            event.remove(db, "do_orm_execute", record_lock)

    assert lock_tables == [
        "users",
        "administrators",
        "departments",
        "assignments",
    ]


def test_cross_college_and_deleted_department_assignments_fail_closed(mutation_data):
    engine, ids = mutation_data
    with Session(engine) as db:
        with pytest.raises(PrivilegedAdministratorMutationDenied):
            stage_department_assignment(
                db,
                ids["users"]["actor"],
                ids["administrators"]["linked"],
                ids["departments"]["other"],
            )
        with pytest.raises(DepartmentMutationTargetNotFound):
            stage_department_assignment(
                db,
                ids["users"]["actor"],
                ids["administrators"]["linked"],
                ids["departments"]["deleted"],
            )


@pytest.mark.parametrize("candidate", ["inactive", "wrong_role"])
def test_identity_link_requires_active_exact_department_admin(
    mutation_data, candidate
):
    engine, ids = mutation_data
    with Session(engine) as db:
        with pytest.raises(PrivilegedAdministratorMutationDenied):
            stage_administrator_identity_change(
                db,
                ids["users"]["actor"],
                ids["administrators"]["unlinked"],
                ids["users"][candidate],
            )


def test_identity_link_and_unlink_are_staged_without_email_inference(mutation_data):
    engine, ids = mutation_data
    with Session(engine) as db:
        administrator = stage_administrator_identity_change(
            db,
            ids["users"]["actor"],
            ids["administrators"]["unlinked"],
            ids["users"]["candidate"],
        )
        assert administrator.user_id == ids["users"]["candidate"]
        administrator = stage_administrator_identity_change(
            db,
            ids["users"]["actor"],
            ids["administrators"]["unlinked"],
            None,
        )
        assert administrator.user_id is None
        db.rollback()


def test_identity_relink_rejects_a_user_already_linked_elsewhere(mutation_data):
    engine, ids = mutation_data
    with Session(engine) as db:
        with pytest.raises(PrivilegedAdministratorMutationDenied):
            stage_administrator_identity_change(
                db,
                ids["users"]["actor"],
                ids["administrators"]["unlinked"],
                ids["users"]["linked"],
            )


def test_assignment_mutation_requires_linked_active_department_admin(mutation_data):
    engine, ids = mutation_data
    with Session(engine) as db:
        with pytest.raises(PrivilegedAdministratorMutationDenied):
            stage_department_assignment(
                db,
                ids["users"]["actor"],
                ids["administrators"]["unlinked"],
                ids["departments"]["first"],
            )


def test_generic_administrator_repository_cannot_relink_identity():
    db = MagicMock(spec=Session)
    repo = DepartmentAdministratorRepository(db)
    administrator = DepartmentAdministrator(
        id="administrator-id",
        name="Administrator",
        email="administrator@example.com",
        role_id="role-id",
        user_id=None,
    )

    with pytest.raises(ValueError, match="privileged administrator mutation service"):
        repo.update(administrator, {"user_id": "untrusted-user"})

    assert administrator.user_id is None
    db.commit.assert_not_called()
