import logging

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool


OLD_PASSWORD = "original-test-password"
NEW_PASSWORD = "replacement-test-password"
WRONG_PASSWORD = "incorrect-test-password"


@pytest.fixture
def password_context(monkeypatch, caplog, capsys):
    # Set safe configuration before importing any CDMS modules. The application's
    # engine cannot point to the development database, even during imports.
    monkeypatch.setenv("DATABASE_URL", "sqlite://")
    monkeypatch.setenv("SECRET_KEY", "isolated-password-change-test-key")
    monkeypatch.setenv("DEBUG", "false")

    from app.api.routers.auth import router
    from app.api.deps.database import get_db
    from app.core.security import create_access_token, hash_password
    from app.models.user import User
    from app.services.auth_service import AuthService

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    User.__table__.create(engine)
    original_hash = hash_password(OLD_PASSWORD)
    with Session(engine) as db:
        user = User(
            email="password-test@example.com",
            hashed_password=original_hash,
            role="super_admin",
            is_active=True,
        )
        db.add(user)
        db.commit()
        user_id = user.id

    def isolated_db():
        with Session(engine) as db:
            yield db

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_db] = isolated_db
    token = create_access_token({"sub": user_id})
    caplog.set_level(logging.DEBUG, logger="app")

    context = {
        "engine": engine,
        "user_model": User,
        "user_id": user_id,
        "original_hash": original_hash,
        "service": AuthService,
        "app": app,
        "headers": {"Authorization": f"Bearer {token}"},
    }
    try:
        yield context
    finally:
        # Check success and failure paths for console/log leakage, including the
        # actual stored hashes rather than only looking for password field names.
        with Session(engine) as db:
            stored_hash = db.get(User, user_id).hashed_password
        app.dependency_overrides.clear()
        engine.dispose()
        captured = capsys.readouterr()
        output = captured.out + captured.err + caplog.text
        for sensitive in (
            OLD_PASSWORD, NEW_PASSWORD, WRONG_PASSWORD, original_hash,
            stored_hash, token, "password-test@example.com",
        ):
            assert sensitive not in output, "Sensitive authentication data was logged"


def stored_password(context):
    # A fresh session ensures assertions check persisted data, not an ORM cache.
    with Session(context["engine"]) as db:
        return db.get(context["user_model"], context["user_id"]).hashed_password


def assert_password_replaced(context):
    from app.core.security import verify_password

    stored_hash = stored_password(context)
    assert stored_hash != context["original_hash"]
    assert stored_hash != NEW_PASSWORD
    assert verify_password(NEW_PASSWORD, stored_hash)
    assert not verify_password(OLD_PASSWORD, stored_hash)


def test_service_changes_password(password_context):
    context = password_context
    with Session(context["engine"]) as db:
        assert context["service"](db).change_password(
            context["user_id"], OLD_PASSWORD, NEW_PASSWORD
        ) is True
    assert_password_replaced(context)


def test_service_rejects_wrong_password_without_changes(password_context):
    context = password_context
    with Session(context["engine"]) as db:
        with pytest.raises(HTTPException) as error:
            context["service"](db).change_password(
                context["user_id"], WRONG_PASSWORD, NEW_PASSWORD
            )
        assert error.value.status_code == 401
        assert not db.dirty
    assert stored_password(context) == context["original_hash"]


def test_service_rejects_missing_user(password_context):
    context = password_context
    with Session(context["engine"]) as db:
        with pytest.raises(HTTPException) as error:
            context["service"](db).change_password(
                "missing-user", OLD_PASSWORD, NEW_PASSWORD
            )
        assert error.value.status_code == 404
    assert stored_password(context) == context["original_hash"]


def test_api_changes_password(password_context):
    context = password_context
    with TestClient(context["app"]) as client:
        response = client.post(
            "/auth/change-password",
            headers=context["headers"],
            json={"current_password": OLD_PASSWORD, "new_password": NEW_PASSWORD},
        )
    assert response.status_code == 200
    assert response.json() == {"message": "Password changed successfully"}
    assert_password_replaced(context)


@pytest.mark.parametrize(
    "current_password,new_password,authenticated,expected_status",
    [
        (WRONG_PASSWORD, NEW_PASSWORD, True, 401),
        (OLD_PASSWORD, "short", True, 422),
        ("short", NEW_PASSWORD, True, 422),
        (OLD_PASSWORD, NEW_PASSWORD, False, 401),
    ],
)
def test_api_rejects_invalid_change_without_changes(
    password_context, current_password, new_password, authenticated, expected_status
):
    context = password_context
    with TestClient(context["app"]) as client:
        response = client.post(
            "/auth/change-password",
            headers=context["headers"] if authenticated else {},
            json={"current_password": current_password, "new_password": new_password},
        )
    assert response.status_code == expected_status
    if authenticated and expected_status == 401:
        assert response.json() == {"detail": "Incorrect email or password"}
        assert response.headers["www-authenticate"] == "Bearer"
    assert stored_password(context) == context["original_hash"]
