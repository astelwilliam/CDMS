import os
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine, event, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateSchema, DropSchema

from app.models.association_tables import department_administrator_departments
from app.models.college import College
from app.models.department import Department
from app.models.department_administrator import DepartmentAdministrator
from app.models.faculty_member import FacultyMember
from app.models.role import Role
from app.models.user import User
from app.repositories.faculty_member_repository import FacultyMemberRepository
from app.repositories.department_administrator_repository import (
    DepartmentAdministratorRepository,
)
from app.repositories.department_repository import DepartmentRepository
from app.services.administrative_deletion import AdministrativeDeletionDisabled
from app.services.scoped_write_authorization import (
    ScopedWriteAccessDenied,
    ScopedWriteResourceNotFound,
    lock_department_write_access,
)
from app.services.privileged_administrator_mutation import (
    stage_administrator_identity_change,
    stage_department_assignment,
    stage_department_assignment_revocation,
)
from app.services.privileged_user_mutation import (
    stage_user_activation_change,
    stage_user_role_change,
)
from app.services.privileged_faculty_mutation import (
    FacultyMutationTargetNotFound,
    PrivilegedFacultyMutationDenied,
    create_faculty_as_super_admin,
    soft_delete_faculty_as_super_admin,
    update_faculty_as_super_admin,
)
from app.core.config import settings


WAIT_SECONDS = 5


@pytest.fixture(scope="module")
def postgres_engine():
    if os.getenv("CDMS_RUN_POSTGRES_CONCURRENCY_TESTS") != "1":
        pytest.skip("set CDMS_RUN_POSTGRES_CONCURRENCY_TESTS=1 to enable")

    database_url = os.getenv("CDMS_POSTGRES_TEST_URL")
    if not database_url:
        pytest.fail("CDMS_POSTGRES_TEST_URL is required")

    parsed_url = make_url(database_url)
    if not parsed_url.drivername.startswith("postgresql"):
        pytest.fail("CDMS_POSTGRES_TEST_URL must use PostgreSQL")
    if not parsed_url.database or "test" not in parsed_url.database.lower():
        pytest.fail("PostgreSQL test database name must contain 'test'")

    configured_urls = [os.getenv("DATABASE_URL"), settings.DATABASE_URL]
    if any(
        configured_url and make_url(configured_url) == parsed_url
        for configured_url in configured_urls
    ):
        pytest.fail("test URL must differ from DATABASE_URL")

    schema_name = f"cdms_concurrency_{uuid.uuid4().hex}"
    administrative_engine = create_engine(database_url, pool_pre_ping=True)
    with administrative_engine.begin() as connection:
        connection.execute(CreateSchema(schema_name))

    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        connect_args={"options": f"-csearch_path={schema_name},public"},
    )

    import app.models  # noqa: F401 - register complete metadata
    from app.db.session import Base

    try:
        Base.metadata.create_all(engine)
        yield engine
    finally:
        engine.dispose()
        with administrative_engine.begin() as connection:
            connection.execute(DropSchema(schema_name, cascade=True))
        administrative_engine.dispose()


@pytest.fixture
def concurrency_data(postgres_engine):
    suffix = uuid.uuid4().hex
    ids = {
        key: str(uuid.uuid4())
        for key in (
            "role",
            "user",
            "new_user",
            "super_user",
            "control_super_user",
            "administrator",
            "college",
            "department",
            "outside_department",
            "deleted_department",
            "faculty",
        )
    }
    with Session(postgres_engine) as db:
        db.add_all(
            [
                Role(id=ids["role"], name=f"role-{suffix}"),
                College(id=ids["college"], name=f"college-{suffix}"),
                User(
                    id=ids["user"],
                    email=f"writer-{suffix}@example.com",
                    hashed_password="unused",
                    role="department_admin",
                    is_active=True,
                ),
                User(
                    id=ids["new_user"],
                    email=f"new-writer-{suffix}@example.com",
                    hashed_password="unused",
                    role="department_admin",
                    is_active=True,
                ),
                User(
                    id=ids["super_user"],
                    email=f"super-{suffix}@example.com",
                    hashed_password="unused",
                    role="super_admin",
                    is_active=True,
                ),
                User(
                    id=ids["control_super_user"],
                    email=f"control-super-{suffix}@example.com",
                    hashed_password="unused",
                    role="super_admin",
                    is_active=True,
                ),
            ]
        )
        db.flush()
        db.add_all(
            [
                Department(
                    id=ids["department"],
                    name="Assigned",
                    college_id=ids["college"],
                ),
                Department(
                    id=ids["outside_department"],
                    name="Outside",
                    college_id=ids["college"],
                ),
                Department(
                    id=ids["deleted_department"],
                    name="Deleted",
                    college_id=ids["college"],
                    deleted_at=datetime.now(timezone.utc),
                ),
            ]
        )
        db.flush()
        db.add(
            DepartmentAdministrator(
                id=ids["administrator"],
                name="Writer",
                email=f"administrator-{suffix}@example.com",
                role_id=ids["role"],
                user_id=ids["user"],
            )
        )
        db.add(
            FacultyMember(
                id=ids["faculty"],
                department_id=ids["department"],
                name="Original",
            )
        )
        db.flush()
        db.execute(
            department_administrator_departments.insert(),
            [
                {
                    "department_administrator_id": ids["administrator"],
                    "department_id": department_id,
                }
                for department_id in (
                    ids["department"],
                    ids["deleted_department"],
                )
            ],
        )
        db.commit()
    return postgres_engine, ids


def set_lock_timeout(db: Session) -> None:
    db.execute(text("SET LOCAL lock_timeout = '3s'"))


def revoke_in_new_session(engine, ids, started: threading.Event) -> bool:
    with Session(engine) as db:
        set_lock_timeout(db)
        started.set()
        revoked = stage_department_assignment_revocation(
            db,
            ids["super_user"],
            ids["administrator"],
            ids["department"],
        )
        db.commit()
        return revoked


def assign_in_new_session(engine, ids, started: threading.Event) -> bool:
    with Session(engine) as db:
        set_lock_timeout(db)
        started.set()
        assigned = stage_department_assignment(
            db,
            ids["super_user"],
            ids["administrator"],
            ids["outside_department"],
        )
        db.commit()
        return assigned


def update_faculty_in_new_session(
    engine,
    ids,
    started: threading.Event,
    name: str,
):
    with Session(engine) as db:
        set_lock_timeout(db)
        started.set()
        return update_faculty_as_super_admin(
            db,
            ids["super_user"],
            ids["faculty"],
            {"name": name},
        )


def test_revocation_first_denies_scoped_mutation(concurrency_data):
    engine, ids = concurrency_data
    with Session(engine) as revocation_db:
        set_lock_timeout(revocation_db)
        assert stage_department_assignment_revocation(
            revocation_db,
            ids["super_user"],
            ids["administrator"],
            ids["department"],
        )
        revocation_db.commit()

    with Session(engine) as write_db:
        set_lock_timeout(write_db)
        with pytest.raises(ScopedWriteResourceNotFound):
            lock_department_write_access(
                write_db, ids["user"], ids["department"]
            )
        write_db.rollback()

    with Session(engine) as verification_db:
        assert verification_db.get(FacultyMember, ids["faculty"]).name == "Original"


def test_write_first_blocks_revocation_until_commit(concurrency_data):
    engine, ids = concurrency_data
    started = threading.Event()
    with Session(engine) as write_db, ThreadPoolExecutor(max_workers=1) as executor:
        set_lock_timeout(write_db)
        lock_department_write_access(write_db, ids["user"], ids["department"])
        repo = FacultyMemberRepository(write_db)
        faculty = repo.get_for_scoped_write(ids["faculty"], ids["department"])
        repo.update_for_scoped_write(faculty, {"name": "Committed first"})

        future = executor.submit(revoke_in_new_session, engine, ids, started)
        assert started.wait(WAIT_SECONDS)
        with pytest.raises(FutureTimeoutError):
            future.result(timeout=0.25)
        write_db.commit()
        assert future.result(timeout=WAIT_SECONDS)

    with Session(engine) as verification_db:
        assert verification_db.get(FacultyMember, ids["faculty"]).name == "Committed first"
        with pytest.raises(ScopedWriteResourceNotFound):
            lock_department_write_access(
                verification_db, ids["user"], ids["department"]
            )


def test_locked_authorization_blocks_assignment_creation_until_commit(
    concurrency_data,
):
    engine, ids = concurrency_data
    started = threading.Event()
    with Session(engine) as authorization_db, ThreadPoolExecutor(max_workers=1) as executor:
        set_lock_timeout(authorization_db)
        lock_department_write_access(
            authorization_db, ids["user"], ids["department"]
        )

        future = executor.submit(assign_in_new_session, engine, ids, started)
        assert started.wait(WAIT_SECONDS)
        with pytest.raises(FutureTimeoutError):
            future.result(timeout=0.25)
        authorization_db.commit()
        assert future.result(timeout=WAIT_SECONDS)

    with Session(engine) as verification_db:
        access = lock_department_write_access(
            verification_db, ids["user"], ids["outside_department"]
        )
        assert access.department.id == ids["outside_department"]


def test_rolled_back_write_does_not_survive_waiting_revocation(concurrency_data):
    engine, ids = concurrency_data
    started = threading.Event()
    with Session(engine) as write_db, ThreadPoolExecutor(max_workers=1) as executor:
        set_lock_timeout(write_db)
        lock_department_write_access(write_db, ids["user"], ids["department"])
        repo = FacultyMemberRepository(write_db)
        faculty = repo.get_for_scoped_write(ids["faculty"], ids["department"])
        repo.update_for_scoped_write(faculty, {"name": "Must roll back"})

        future = executor.submit(revoke_in_new_session, engine, ids, started)
        assert started.wait(WAIT_SECONDS)
        with pytest.raises(FutureTimeoutError):
            future.result(timeout=0.25)
        write_db.rollback()
        assert future.result(timeout=WAIT_SECONDS)

    with Session(engine) as verification_db:
        assert verification_db.get(FacultyMember, ids["faculty"]).name == "Original"


@pytest.mark.parametrize(
    "changes",
    [{"role": "super_admin"}, {"is_active": False}],
)
def test_account_change_waits_for_locked_authorization_then_takes_effect(
    concurrency_data, changes
):
    engine, ids = concurrency_data
    started = threading.Event()

    def change_account():
        with Session(engine) as db:
            set_lock_timeout(db)
            started.set()
            if "role" in changes:
                stage_user_role_change(
                    db,
                    ids["super_user"],
                    ids["user"],
                    changes["role"],
                )
            else:
                stage_user_activation_change(
                    db,
                    ids["super_user"],
                    ids["user"],
                    changes["is_active"],
                )
            db.commit()

    with Session(engine) as authorization_db, ThreadPoolExecutor(max_workers=1) as executor:
        set_lock_timeout(authorization_db)
        lock_department_write_access(
            authorization_db, ids["user"], ids["department"]
        )
        future = executor.submit(change_account)
        assert started.wait(WAIT_SECONDS)
        with pytest.raises(FutureTimeoutError):
            future.result(timeout=0.25)
        authorization_db.commit()
        future.result(timeout=WAIT_SECONDS)

    with Session(engine) as verification_db:
        with pytest.raises(ScopedWriteAccessDenied):
            lock_department_write_access(
                verification_db, ids["user"], ids["department"]
            )


def test_identity_relink_waits_for_locked_authorization(concurrency_data):
    engine, ids = concurrency_data
    started = threading.Event()

    def relink_identity():
        with Session(engine) as db:
            set_lock_timeout(db)
            started.set()
            stage_administrator_identity_change(
                db,
                ids["super_user"],
                ids["administrator"],
                ids["new_user"],
            )
            db.commit()

    with Session(engine) as authorization_db, ThreadPoolExecutor(max_workers=1) as executor:
        set_lock_timeout(authorization_db)
        lock_department_write_access(
            authorization_db, ids["user"], ids["department"]
        )
        future = executor.submit(relink_identity)
        assert started.wait(WAIT_SECONDS)
        with pytest.raises(FutureTimeoutError):
            future.result(timeout=0.25)
        authorization_db.commit()
        future.result(timeout=WAIT_SECONDS)

    with Session(engine) as verification_db:
        with pytest.raises(ScopedWriteAccessDenied):
            lock_department_write_access(
                verification_db, ids["user"], ids["department"]
            )
        verification_db.rollback()

    with Session(engine) as verification_db:
        access = lock_department_write_access(
            verification_db, ids["new_user"], ids["department"]
        )
        assert access.administrator.id == ids["administrator"]


def test_cross_department_and_soft_deleted_department_are_denied(concurrency_data):
    engine, ids = concurrency_data
    with Session(engine) as db:
        with pytest.raises(ScopedWriteResourceNotFound):
            lock_department_write_access(
                db, ids["user"], ids["outside_department"]
            )
        with pytest.raises(ScopedWriteResourceNotFound):
            lock_department_write_access(
                db, ids["user"], ids["deleted_department"]
            )


@pytest.mark.parametrize(
    "mutation",
    ["role", "deactivation"],
)
def test_committed_account_change_denies_waiting_production_faculty_write(
    concurrency_data, mutation
):
    engine, ids = concurrency_data
    started = threading.Event()

    with Session(engine) as account_db, ThreadPoolExecutor(max_workers=1) as executor:
        set_lock_timeout(account_db)
        if mutation == "role":
            stage_user_role_change(
                account_db,
                ids["control_super_user"],
                ids["super_user"],
                "department_admin",
            )
        else:
            stage_user_activation_change(
                account_db,
                ids["control_super_user"],
                ids["super_user"],
                False,
            )

        future = executor.submit(
            update_faculty_in_new_session,
            engine,
            ids,
            started,
            "Must Be Denied",
        )
        assert started.wait(WAIT_SECONDS)
        with pytest.raises(FutureTimeoutError):
            future.result(timeout=0.25)
        account_db.commit()
        with pytest.raises(PrivilegedFacultyMutationDenied):
            future.result(timeout=WAIT_SECONDS)

    with Session(engine) as verification_db:
        assert verification_db.get(FacultyMember, ids["faculty"]).name == "Original"


def test_production_faculty_update_waits_for_department_lock(concurrency_data):
    engine, ids = concurrency_data
    started = threading.Event()

    with Session(engine) as department_db, ThreadPoolExecutor(max_workers=1) as executor:
        set_lock_timeout(department_db)
        department_db.scalar(
            select(Department)
            .where(Department.id == ids["department"])
            .with_for_update()
        )
        future = executor.submit(
            update_faculty_in_new_session,
            engine,
            ids,
            started,
            "Committed After Department Lock",
        )
        assert started.wait(WAIT_SECONDS)
        with pytest.raises(FutureTimeoutError):
            future.result(timeout=0.25)
        department_db.commit()
        faculty = future.result(timeout=WAIT_SECONDS)
        assert faculty.name == "Committed After Department Lock"

    with Session(engine) as verification_db:
        assert (
            verification_db.get(FacultyMember, ids["faculty"]).name
            == "Committed After Department Lock"
        )


def test_production_soft_delete_waits_for_faculty_lock(concurrency_data):
    engine, ids = concurrency_data
    started = threading.Event()

    def soft_delete_in_new_session():
        with Session(engine) as db:
            set_lock_timeout(db)
            started.set()
            soft_delete_faculty_as_super_admin(
                db, ids["super_user"], ids["faculty"]
            )

    with Session(engine) as faculty_db, ThreadPoolExecutor(max_workers=1) as executor:
        faculty_db.scalar(
            select(FacultyMember)
            .where(FacultyMember.id == ids["faculty"])
            .with_for_update()
        )
        future = executor.submit(soft_delete_in_new_session)
        assert started.wait(WAIT_SECONDS)
        with pytest.raises(FutureTimeoutError):
            future.result(timeout=0.25)
        faculty_db.commit()
        future.result(timeout=WAIT_SECONDS)

    with Session(engine) as verification_db:
        faculty = verification_db.get(FacultyMember, ids["faculty"])
        assert faculty is not None
        assert faculty.deleted_at is not None


def test_production_faculty_lock_timeout_rolls_back(concurrency_data):
    engine, ids = concurrency_data
    started = threading.Event()

    with Session(engine) as department_db, ThreadPoolExecutor(max_workers=1) as executor:
        department_db.scalar(
            select(Department)
            .where(Department.id == ids["department"])
            .with_for_update()
        )
        future = executor.submit(
            update_faculty_in_new_session,
            engine,
            ids,
            started,
            "Must Roll Back After Timeout",
        )
        assert started.wait(WAIT_SECONDS)
        with pytest.raises(OperationalError) as error:
            future.result(timeout=WAIT_SECONDS)
        sqlstate = getattr(error.value.orig, "sqlstate", None) or getattr(
            error.value.orig, "pgcode", None
        )
        assert sqlstate == "55P03"
        department_db.rollback()

    with Session(engine) as verification_db:
        assert verification_db.get(FacultyMember, ids["faculty"]).name == "Original"


def test_production_faculty_service_uses_global_lock_order(concurrency_data):
    engine, ids = concurrency_data
    locked_tables = []

    with Session(engine) as db:
        def record_lock(execute_state):
            statement = execute_state.statement
            if getattr(statement, "_for_update_arg", None) is None:
                return
            sql = " ".join(statement.compile().string.lower().split())
            for table_name, label in (
                ("users", "users"),
                ("departments", "departments"),
                ("faculty_members", "faculty"),
            ):
                if f" from {table_name} " in f" {sql} ":
                    locked_tables.append(label)
                    break

        event.listen(db, "do_orm_execute", record_lock)
        try:
            update_faculty_as_super_admin(
                db,
                ids["super_user"],
                ids["faculty"],
                {"name": "Lock Order Verified"},
            )
        finally:
            event.remove(db, "do_orm_execute", record_lock)

    assert locked_tables == ["users", "departments", "faculty"]


def test_production_create_rejects_deleted_department_without_partial_insert(
    concurrency_data,
):
    engine, ids = concurrency_data
    with Session(engine) as db:
        with pytest.raises(FacultyMutationTargetNotFound):
            create_faculty_as_super_admin(
                db,
                ids["super_user"],
                ids["deleted_department"],
                {"name": "Must Not Be Created"},
            )
        assert not db.in_transaction()

    with Session(engine) as verification_db:
        assert verification_db.scalar(
            select(FacultyMember.id).where(
                FacultyMember.name == "Must Not Be Created"
            )
        ) is None


def test_administrative_deletion_guards_preserve_related_rows(concurrency_data):
    engine, ids = concurrency_data
    with Session(engine) as db:
        with pytest.raises(AdministrativeDeletionDisabled):
            DepartmentRepository(db).delete(ids["department"])
        with pytest.raises(AdministrativeDeletionDisabled):
            DepartmentAdministratorRepository(db).delete(ids["administrator"])
        db.rollback()

    with Session(engine) as verification_db:
        assert verification_db.get(Department, ids["department"]) is not None
        assert (
            verification_db.get(
                DepartmentAdministrator, ids["administrator"]
            )
            is not None
        )
        assert verification_db.get(FacultyMember, ids["faculty"]) is not None
        assert verification_db.scalar(
            select(department_administrator_departments.c.department_id).where(
                department_administrator_departments.c.department_administrator_id
                == ids["administrator"],
                department_administrator_departments.c.department_id
                == ids["department"],
            )
        ) == ids["department"]
