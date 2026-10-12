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
from app.services.scoped_write_authorization import (
    ScopedWriteAccessDenied,
    ScopedWriteResourceNotFound,
    lock_department_write_access,
)
from app.services.privileged_administrator_mutation import (
    stage_department_assignment_revocation,
)


@pytest.fixture
def authorization_data():
    import app.models  # noqa: F401 - register complete relationship metadata
    from app.db.session import Base

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        role = Role(name="scoped-write-role")
        college = College(name="Scoped Write College")
        other_college = College(name="Other Scoped Write College")
        user = User(
            email="scoped-write@example.com",
            hashed_password="unused",
            role="department_admin",
            is_active=True,
        )
        super_user = User(
            email="scoped-write-super@example.com",
            hashed_password="unused",
            role="super_admin",
            is_active=True,
        )
        db.add_all([role, college, other_college, user, super_user])
        db.flush()
        departments = {
            "first": Department(name="First", college_id=college.id),
            "second": Department(name="Second", college_id=college.id),
            "other": Department(name="Other", college_id=other_college.id),
            "deleted": Department(name="Deleted", college_id=college.id),
        }
        db.add_all(departments.values())
        db.flush()
        administrator = DepartmentAdministrator(
            name="Scoped Writer",
            email="scoped-writer@example.com",
            role_id=role.id,
            user_id=user.id,
        )
        db.add(administrator)
        db.flush()
        db.execute(
            department_administrator_departments.insert(),
            [
                {
                    "department_administrator_id": administrator.id,
                    "department_id": departments[name].id,
                }
                for name in ("first", "second")
            ],
        )
        db.commit()
        ids = {
            "user": user.id,
            "super_user": super_user.id,
            "administrator": administrator.id,
            "departments": {name: value.id for name, value in departments.items()},
        }

    yield engine, ids
    engine.dispose()


def test_valid_assignment_locks_and_returns_current_database_identity(
    authorization_data,
):
    engine, ids = authorization_data
    with Session(engine) as db:
        access = lock_department_write_access(
            db, ids["user"], ids["departments"]["first"]
        )
        assert access.user.id == ids["user"]
        assert access.administrator.id == ids["administrator"]
        assert access.department.id == ids["departments"]["first"]
        assert db.in_transaction()


def test_lock_order_is_user_admin_department_assignment(authorization_data):
    engine, ids = authorization_data
    lock_tables = []

    with Session(engine) as db:
        def record_lock(execute_state):
            statement = execute_state.statement
            if getattr(statement, "_for_update_arg", None) is None:
                return
            sql = " ".join(statement.compile().string.lower().split())
            if " from users " in f" {sql} ":
                lock_tables.append("users")
            elif " from department_administrators " in f" {sql} ":
                lock_tables.append("administrators")
            elif " from departments " in f" {sql} ":
                lock_tables.append("departments")
            elif " from department_administrator_departments " in f" {sql} ":
                lock_tables.append("assignments")

        event.listen(db, "do_orm_execute", record_lock)
        try:
            lock_department_write_access(
                db, ids["user"], ids["departments"]["first"]
            )
        finally:
            event.remove(db, "do_orm_execute", record_lock)

    assert lock_tables == [
        "users",
        "administrators",
        "departments",
        "assignments",
    ]


def test_missing_or_revoked_assignment_is_denied(authorization_data):
    engine, ids = authorization_data
    with Session(engine) as db:
        with pytest.raises(ScopedWriteResourceNotFound):
            lock_department_write_access(
                db, ids["user"], ids["departments"]["other"]
            )

        assert stage_department_assignment_revocation(
            db,
            ids["super_user"],
            ids["administrator"],
            ids["departments"]["first"],
        )
        db.commit()

    with Session(engine) as db:
        with pytest.raises(ScopedWriteResourceNotFound):
            lock_department_write_access(
                db, ids["user"], ids["departments"]["first"]
            )


@pytest.mark.parametrize(
    "field,value",
    [("is_active", False), ("role", "super_admin")],
)
def test_current_user_status_and_exact_role_are_revalidated(
    authorization_data, field, value
):
    engine, ids = authorization_data
    with Session(engine) as db:
        setattr(db.get(User, ids["user"]), field, value)
        db.commit()
    with Session(engine) as db:
        with pytest.raises(ScopedWriteAccessDenied):
            lock_department_write_access(
                db, ids["user"], ids["departments"]["first"]
            )


def test_removed_identity_link_is_denied(authorization_data):
    engine, ids = authorization_data
    with Session(engine) as db:
        db.get(DepartmentAdministrator, ids["administrator"]).user_id = None
        db.commit()
    with Session(engine) as db:
        with pytest.raises(ScopedWriteAccessDenied):
            lock_department_write_access(
                db, ids["user"], ids["departments"]["first"]
            )


def test_deleted_department_is_hidden(authorization_data):
    engine, ids = authorization_data
    from datetime import datetime, timezone

    with Session(engine) as db:
        db.get(Department, ids["departments"]["first"]).deleted_at = datetime.now(
            timezone.utc
        )
        db.commit()
    with Session(engine) as db:
        with pytest.raises(ScopedWriteResourceNotFound):
            lock_department_write_access(
                db, ids["user"], ids["departments"]["first"]
            )


def test_cross_college_assignment_fails_closed(authorization_data):
    engine, ids = authorization_data
    with Session(engine) as db:
        db.execute(
            department_administrator_departments.insert(),
            {
                "department_administrator_id": ids["administrator"],
                "department_id": ids["departments"]["other"],
            },
        )
        db.commit()
    with Session(engine) as db:
        with pytest.raises(ScopedWriteAccessDenied):
            lock_department_write_access(
                db, ids["user"], ids["departments"]["first"]
            )


def test_revocation_uses_compatible_order_and_never_commits(authorization_data):
    engine, ids = authorization_data
    with Session(engine) as db:
        assert stage_department_assignment_revocation(
            db,
            ids["super_user"],
            ids["administrator"],
            ids["departments"]["first"],
        )
        db.rollback()

    with Session(engine) as db:
        assignment_exists = db.scalar(
            select(department_administrator_departments.c.department_id).where(
                department_administrator_departments.c.department_administrator_id
                == ids["administrator"],
                department_administrator_departments.c.department_id
                == ids["departments"]["first"],
            )
        )
        assert assignment_exists == ids["departments"]["first"]
