import os
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine, select, text
from sqlalchemy.engine import make_url
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
from app.services.scoped_write_authorization import (
    ScopedWriteAccessDenied,
    ScopedWriteResourceNotFound,
    lock_department_write_access,
    revoke_department_assignment,
)
from app.services.privileged_user_mutation import (
    stage_user_activation_change,
    stage_user_role_change,
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
        revoked = revoke_department_assignment(
            db,
            ids["user"],
            ids["administrator"],
            ids["department"],
        )
        db.commit()
        return revoked


def test_revocation_first_denies_scoped_mutation(concurrency_data):
    engine, ids = concurrency_data
    with Session(engine) as revocation_db:
        set_lock_timeout(revocation_db)
        assert revoke_department_assignment(
            revocation_db,
            ids["user"],
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
            users = list(
                db.scalars(
                    select(User)
                    .where(User.id.in_([ids["user"], ids["new_user"]]))
                    .order_by(User.id)
                    .with_for_update()
                )
            )
            assert len(users) == 2
            administrator = db.scalar(
                select(DepartmentAdministrator)
                .where(DepartmentAdministrator.id == ids["administrator"])
                .with_for_update()
            )
            assert administrator.user_id == ids["user"]
            administrator.user_id = ids["new_user"]
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
