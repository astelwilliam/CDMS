from datetime import timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool


PASSWORD = "account-status-test-password"
EMAIL = "account-status@example.com"


@pytest.fixture
def account(monkeypatch):
    # Configure imports safely; every API request uses a fresh isolated session.
    monkeypatch.setenv("DATABASE_URL", "sqlite://")
    monkeypatch.setenv("SECRET_KEY", "isolated-account-status-test-key")
    monkeypatch.setenv("DEBUG", "false")

    from app.api.deps.database import get_db
    from app.api.routers.auth import router
    from app.core.security import hash_password
    from app.models.user import User

    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    User.__table__.create(engine)
    with Session(engine) as db:
        user = User(
            email=EMAIL, hashed_password=hash_password(PASSWORD),
            role="super_admin", is_active=True,
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
    try:
        with TestClient(app) as client:
            yield {"client": client, "engine": engine, "model": User, "id": user_id}
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def set_active(account, active):
    with Session(account["engine"]) as db:
        db.get(account["model"], account["id"]).is_active = active
        db.commit()


def login(account, password=PASSWORD):
    return account["client"].post(
        "/auth/login", data={"username": EMAIL, "password": password}
    )


def login_headers(account):
    response = login(account)
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def assert_rejected(response, detail="Could not validate credentials"):
    assert response.status_code == 401
    assert response.json() == {"detail": detail}
    assert response.headers["www-authenticate"] == "Bearer"


def test_active_user_can_login_and_access_me(account):
    response = account["client"].get("/auth/me", headers=login_headers(account))
    assert response.status_code == 200
    assert response.json() == {
        "id": account["id"], "email": EMAIL, "role": "super_admin", "is_active": True
    }


@pytest.mark.parametrize("password", [PASSWORD, "incorrect-password"])
def test_inactive_login_uses_generic_credentials_error(account, password):
    set_active(account, False)
    assert_rejected(login(account, password), "Incorrect email or password")


def test_existing_token_obeys_deactivation_and_reactivation(account):
    headers = login_headers(account)
    set_active(account, False)
    assert_rejected(account["client"].get("/auth/me", headers=headers))

    # The same token also cannot reach the password-changing operation.
    with Session(account["engine"]) as db:
        original_hash = db.get(account["model"], account["id"]).hashed_password
    assert_rejected(account["client"].post(
        "/auth/change-password", headers=headers,
        json={"current_password": PASSWORD, "new_password": "replacement-password"},
    ))
    with Session(account["engine"]) as db:
        assert db.get(account["model"], account["id"]).hashed_password == original_hash

    set_active(account, True)
    response = account["client"].get("/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["is_active"] is True


def test_inactive_database_status_overrides_active_token_claim(account):
    from app.core.security import create_access_token

    token = create_access_token({"sub": account["id"], "is_active": True})
    set_active(account, False)
    assert_rejected(account["client"].get(
        "/auth/me", headers={"Authorization": f"Bearer {token}"}
    ))


def test_token_for_deleted_user_is_rejected(account):
    headers = login_headers(account)
    with Session(account["engine"]) as db:
        db.delete(db.get(account["model"], account["id"]))
        db.commit()
    assert_rejected(account["client"].get("/auth/me", headers=headers))


@pytest.mark.parametrize("kind", ["malformed", "wrong_signature", "expired"])
def test_invalid_or_expired_token_is_rejected(account, kind):
    from jose import jwt
    from app.core.config import settings
    from app.core.security import create_access_token

    if kind == "malformed":
        token = "not-a-jwt"
    elif kind == "wrong_signature":
        token = jwt.encode(
            {"sub": account["id"]}, "different-test-signing-key",
            algorithm=settings.ALGORITHM,
        )
    else:
        token = create_access_token(
            {"sub": account["id"]}, expires_delta=timedelta(minutes=-1)
        )
    assert_rejected(account["client"].get(
        "/auth/me", headers={"Authorization": f"Bearer {token}"}
    ))
