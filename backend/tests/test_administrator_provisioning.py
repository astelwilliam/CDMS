from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.security import verify_password
from app.db.session import Base
from app.models.user import User
from app.services.administrator_provisioning import (
    AdministratorAlreadyProvisioned,
    AdministratorEmailUnavailable,
    InvalidAdministratorCredentials,
    stage_initial_super_administrator,
)
from seed_admin import provision_super_admin


PASSWORD = "bootstrap-test-password"


@pytest.fixture
def session_factory():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine, tables=[User.__table__])
    factory = sessionmaker(bind=engine)
    try:
        yield factory
    finally:
        engine.dispose()


def test_service_stages_first_super_admin_without_internal_commit(session_factory):
    db = session_factory()
    try:
        administrator = stage_initial_super_administrator(
            db,
            "First.Admin@Example.com",
            PASSWORD,
        )

        assert administrator.email == "first.admin@example.com"
        assert administrator.role == "super_admin"
        assert administrator.is_active is True
        assert administrator.hashed_password != PASSWORD
        assert verify_password(PASSWORD, administrator.hashed_password)

        db.rollback()
        assert db.scalar(select(User.id)) is None
    finally:
        db.close()


def test_existing_super_admin_fails_without_creating_another(session_factory):
    db = session_factory()
    try:
        existing = User(
            email="existing@example.com",
            hashed_password="unused",
            role="super_admin",
            is_active=False,
        )
        db.add(existing)
        db.commit()

        with pytest.raises(AdministratorAlreadyProvisioned):
            stage_initial_super_administrator(
                db,
                "second@example.com",
                PASSWORD,
            )

        assert list(db.scalars(select(User))) == [existing]
    finally:
        db.close()


def test_existing_email_identity_fails_closed(session_factory):
    db = session_factory()
    try:
        existing = User(
            email="claimed@example.com",
            hashed_password="unchanged",
            role="department_admin",
            is_active=True,
        )
        db.add(existing)
        db.commit()

        with pytest.raises(AdministratorEmailUnavailable):
            stage_initial_super_administrator(
                db,
                "CLAIMED@example.com",
                PASSWORD,
            )

        db.refresh(existing)
        assert existing.role == "department_admin"
        assert existing.hashed_password == "unchanged"
    finally:
        db.close()


@pytest.mark.parametrize(
    "email,password",
    [("not-an-email", PASSWORD), ("admin@example.com", "short")],
)
def test_invalid_credentials_fail_before_database_mutation(
    session_factory,
    email,
    password,
):
    db = session_factory()
    try:
        with pytest.raises(InvalidAdministratorCredentials):
            stage_initial_super_administrator(db, email, password)

        assert not db.new
        assert db.scalar(select(User.id)) is None
    finally:
        db.close()


def test_cli_commits_valid_identity_without_disclosing_credentials(
    session_factory,
    capsys,
):
    prompts = iter([PASSWORD, PASSWORD])

    result = provision_super_admin(
        session_factory=session_factory,
        input_fn=lambda _prompt: "admin@example.com",
        password_fn=lambda _prompt: next(prompts),
    )

    assert result == 0
    db = session_factory()
    try:
        administrator = db.scalar(select(User))
        assert administrator is not None
        assert verify_password(PASSWORD, administrator.hashed_password)
    finally:
        db.close()

    output = capsys.readouterr()
    assert PASSWORD not in output.out
    assert PASSWORD not in output.err
    assert administrator.hashed_password not in output.out
    assert administrator.hashed_password not in output.err


def test_cli_existing_admin_is_idempotent_and_does_not_prompt(
    session_factory,
    capsys,
):
    db = session_factory()
    db.add(
        User(
            email="existing@example.com",
            hashed_password="unused",
            role="super_admin",
            is_active=True,
        )
    )
    db.commit()
    db.close()

    password_fn = MagicMock(side_effect=AssertionError("must not prompt"))
    result = provision_super_admin(
        session_factory=session_factory,
        input_fn=MagicMock(side_effect=AssertionError("must not prompt")),
        password_fn=password_fn,
    )

    assert result == 0
    password_fn.assert_not_called()
    assert "already provisioned" in capsys.readouterr().out


def test_cli_rolls_back_and_hides_database_errors(capsys):
    db = MagicMock(spec=Session)
    db.scalar.side_effect = RuntimeError("sensitive database details")
    factory = MagicMock(return_value=db)

    result = provision_super_admin(session_factory=factory)

    assert result == 1
    db.rollback.assert_called_once_with()
    db.close.assert_called_once_with()
    output = capsys.readouterr()
    assert "sensitive database details" not in output.err


def test_no_public_administrator_registration_route():
    from app.main import app

    public_paths = {
        route.path
        for route in app.routes
        if route.path.startswith("/auth/")
    }
    assert "/auth/register" not in public_paths
    assert "/auth/signup" not in public_paths
