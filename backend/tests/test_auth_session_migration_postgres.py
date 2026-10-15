import os
import subprocess
import sys
import uuid
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError
from sqlalchemy.schema import CreateSchema, DropSchema


BACKEND_ROOT = Path(__file__).resolve().parents[1]
BASE_REVISION = "b71f0c1d2026"
SESSION_REVISION = "e4a8c1f73b29"


def run_alembic(database_url: str, *arguments: str) -> None:
    environment = os.environ.copy()
    environment.update(
        DATABASE_URL=database_url,
        SECRET_KEY="isolated-auth-session-migration-key",
        DEBUG="false",
    )
    result = subprocess.run(
        [sys.executable, "-B", "-m", "alembic", "-c", "alembic.ini", *arguments],
        cwd=BACKEND_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        f"Alembic {' '.join(arguments)} failed with exit code "
        f"{result.returncode}: {result.stderr[-2000:]}"
    )


@pytest.fixture(scope="module")
def migration_database():
    if os.getenv("CDMS_RUN_POSTGRES_MIGRATION_TESTS") != "1":
        pytest.skip("set CDMS_RUN_POSTGRES_MIGRATION_TESTS=1 to enable")

    database_url = os.getenv("CDMS_POSTGRES_TEST_URL")
    if not database_url:
        pytest.fail("CDMS_POSTGRES_TEST_URL is required")
    parsed = make_url(database_url)
    if not parsed.drivername.startswith("postgresql"):
        pytest.fail("migration test URL must use PostgreSQL")
    if not parsed.database or "test" not in parsed.database.lower():
        pytest.fail("migration test database name must contain 'test'")

    configured = os.getenv("DATABASE_URL")
    if configured and make_url(configured) == parsed:
        pytest.fail("migration test URL must differ from DATABASE_URL")

    schema_name = f"cdms_session_migration_{uuid.uuid4().hex}"
    administrative_engine = create_engine(database_url, pool_pre_ping=True)
    with administrative_engine.begin() as connection:
        connection.execute(CreateSchema(schema_name))

    scoped_url = parsed.update_query_dict(
        {"options": f"-csearch_path={schema_name}"}
    ).render_as_string(hide_password=False)
    engine = create_engine(scoped_url, pool_pre_ping=True)
    try:
        yield engine, scoped_url, schema_name
    finally:
        engine.dispose()
        with administrative_engine.begin() as connection:
            connection.execute(DropSchema(schema_name, cascade=True))
        administrative_engine.dispose()


def test_auth_session_migration_preserves_existing_data(migration_database):
    engine, database_url, schema_name = migration_database
    run_alembic(database_url, "upgrade", BASE_REVISION)

    user_id = str(uuid.uuid4())
    with engine.begin() as connection:
        assert connection.scalar(text("SELECT current_schema()")) == schema_name
        connection.execute(
            text(
                "INSERT INTO users "
                "(id, email, hashed_password, role, is_active, created_at, updated_at) "
                "VALUES (:id, :email, 'unused', 'super_admin', true, now(), now())"
            ),
            {"id": user_id, "email": f"session-{uuid.uuid4().hex}@example.invalid"},
        )
        before = connection.scalar(
            text(
                "SELECT md5(id || ':' || email || ':' || role || ':' || is_active) "
                "FROM users WHERE id=:id"
            ),
            {"id": user_id},
        )
        assert connection.scalar(
            text(
                "SELECT count(*) FROM information_schema.tables "
                "WHERE table_schema=current_schema() AND table_name='auth_sessions'"
            )
        ) == 0

    run_alembic(database_url, "upgrade", SESSION_REVISION)
    with engine.begin() as connection:
        assert connection.scalar(text("SELECT version_num FROM alembic_version")) == (
            SESSION_REVISION
        )
        after = connection.scalar(
            text(
                "SELECT md5(id || ':' || email || ':' || role || ':' || is_active) "
                "FROM users WHERE id=:id"
            ),
            {"id": user_id},
        )
        assert after == before
        assert connection.scalar(
            text(
                "SELECT count(*) FROM information_schema.columns "
                "WHERE table_schema=current_schema() AND table_name='auth_sessions'"
            )
        ) == 7
        constraints = dict(
            connection.execute(
                text(
                    "SELECT conname, contype::text FROM pg_constraint c "
                    "JOIN pg_class t ON t.oid=c.conrelid "
                    "JOIN pg_namespace n ON n.oid=t.relnamespace "
                    "WHERE n.nspname=current_schema() AND t.relname='auth_sessions'"
                )
            ).tuples().all()
        )
        assert constraints["uq_auth_sessions_token_hash"] == "u"
        assert constraints["fk_auth_sessions_user_id_users"] == "f"

        connection.execute(
            text(
                "INSERT INTO auth_sessions "
                "(id, user_id, token_hash, expires_at, created_at, updated_at) "
                "VALUES (:id, :user_id, :token_hash, now() + interval '1 hour', "
                "now(), now())"
            ),
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "token_hash": "a" * 64,
            },
        )

    with pytest.raises(IntegrityError):
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO auth_sessions "
                    "(id, user_id, token_hash, expires_at, created_at, updated_at) "
                    "VALUES (:id, :user_id, :token_hash, now() + interval '1 hour', "
                    "now(), now())"
                ),
                {
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "token_hash": "a" * 64,
                },
            )

    with pytest.raises(IntegrityError):
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO auth_sessions "
                    "(id, user_id, token_hash, expires_at, created_at, updated_at) "
                    "VALUES (:id, :user_id, :token_hash, now() + interval '1 hour', "
                    "now(), now())"
                ),
                {
                    "id": str(uuid.uuid4()),
                    "user_id": str(uuid.uuid4()),
                    "token_hash": "b" * 64,
                },
            )

    run_alembic(database_url, "downgrade", BASE_REVISION)
    with engine.begin() as connection:
        assert connection.scalar(text("SELECT version_num FROM alembic_version")) == (
            BASE_REVISION
        )
        assert connection.scalar(
            text("SELECT count(*) FROM users WHERE id=:id"), {"id": user_id}
        ) == 1
        assert connection.scalar(
            text(
                "SELECT count(*) FROM information_schema.tables "
                "WHERE table_schema=current_schema() AND table_name='auth_sessions'"
            )
        ) == 0

    run_alembic(database_url, "upgrade", SESSION_REVISION)
    run_alembic(database_url, "check")
    with engine.begin() as connection:
        assert connection.scalar(text("SELECT version_num FROM alembic_version")) == (
            SESSION_REVISION
        )
        assert connection.scalar(text("SELECT count(*) FROM auth_sessions")) == 0
        assert connection.scalar(
            text("SELECT count(*) FROM users WHERE id=:id"), {"id": user_id}
        ) == 1
