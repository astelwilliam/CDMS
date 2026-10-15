from datetime import datetime, timedelta, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool


ORIGIN = "http://frontend.test"
PASSWORD = "persistent-session-password"


@pytest.fixture
def session_app(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite://")
    monkeypatch.setenv("SECRET_KEY", "isolated-persistent-session-key")
    monkeypatch.setenv("DEBUG", "false")

    from app.api.deps.database import get_db
    from app.api.routers.auth import router
    from app.core.config import settings
    from app.core.security import hash_password
    from app.middleware.csrf import CSRFMiddleware
    from app.models.auth_session import AuthSession
    from app.models.user import User

    monkeypatch.setattr(settings, "BACKEND_CORS_ORIGINS", [ORIGIN])
    monkeypatch.setattr(settings, "SESSION_COOKIE_SECURE", False)
    monkeypatch.setattr(settings, "SESSION_EXPIRE_MINUTES", 60)

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    User.__table__.create(engine)
    AuthSession.__table__.create(engine)

    users = {}
    with Session(engine) as db:
        for role, active in (
            ("super_admin", True),
            ("department_admin", True),
            ("student", True),
            ("inactive", False),
        ):
            user = User(
                email=f"{role}@example.com",
                hashed_password=hash_password(PASSWORD),
                role="super_admin" if role == "inactive" else role,
                is_active=active,
            )
            db.add(user)
            db.flush()
            users[role] = user.id
        db.commit()

    def isolated_db():
        with Session(engine) as db:
            yield db

    app = FastAPI()
    app.add_middleware(CSRFMiddleware)
    app.include_router(router)
    app.dependency_overrides[get_db] = isolated_db
    try:
        with TestClient(app) as client:
            yield {
                "client": client,
                "engine": engine,
                "session_model": AuthSession,
                "user_model": User,
                "users": users,
                "settings": settings,
            }
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def login(context, role="super_admin", origin=ORIGIN):
    return context["client"].post(
        "/auth/session/login",
        headers={"Origin": origin},
        data={"username": f"{role}@example.com", "password": PASSWORD},
    )


def test_session_login_hashes_token_and_sets_guarded_cookie(session_app):
    response = login(session_app)
    assert response.status_code == 200
    cookie = response.headers["set-cookie"]
    assert "cdms_session=" in cookie
    assert "HttpOnly" in cookie
    assert "SameSite=lax" in cookie
    assert "Secure" not in cookie
    assert "Domain=" not in cookie

    raw_token = session_app["client"].cookies.get("cdms_session")
    assert raw_token
    assert raw_token not in response.text
    with Session(session_app["engine"]) as db:
        stored = db.scalar(select(session_app["session_model"]))
        assert stored.token_hash != raw_token
        assert len(stored.token_hash) == 64
        assert stored.user_id == session_app["users"]["super_admin"]


def test_secure_cookie_flag_is_configurable_for_https(session_app, monkeypatch):
    monkeypatch.setattr(session_app["settings"], "SESSION_COOKIE_SECURE", True)
    response = login(session_app)
    assert response.status_code == 200
    assert "Secure" in response.headers["set-cookie"]


def test_session_restores_after_a_new_request(session_app):
    login_response = login(session_app)
    csrf_token = login_response.json()["csrf_token"]
    response = session_app["client"].get("/auth/session")
    assert response.status_code == 200
    assert response.json()["user"]["role"] == "super_admin"
    assert response.json()["csrf_token"] == csrf_token


def test_logout_revokes_session_and_clears_cookie(session_app):
    csrf_token = login(session_app).json()["csrf_token"]
    raw_token = session_app["client"].cookies.get("cdms_session")
    response = session_app["client"].post(
        "/auth/session/logout",
        headers={"Origin": ORIGIN, "X-CSRF-Token": csrf_token},
    )
    assert response.status_code == 204
    assert session_app["client"].cookies.get("cdms_session") is None

    from app.services.session_service import hash_session_token

    with Session(session_app["engine"]) as db:
        stored = db.scalar(
            select(session_app["session_model"]).where(
                session_app["session_model"].token_hash
                == hash_session_token(raw_token)
            )
        )
        assert stored.revoked_at is not None

    session_app["client"].cookies.set("cdms_session", raw_token)
    assert session_app["client"].get("/auth/session").status_code == 401


def test_expired_session_cannot_authenticate(session_app):
    assert login(session_app).status_code == 200
    with Session(session_app["engine"]) as db:
        stored = db.scalar(select(session_app["session_model"]))
        stored.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        db.commit()
    assert session_app["client"].get("/auth/session").status_code == 401


def test_role_change_invalidates_administrator_session(session_app):
    assert login(session_app).status_code == 200
    with Session(session_app["engine"]) as db:
        user = db.get(
            session_app["user_model"],
            session_app["users"]["super_admin"],
        )
        user.role = "student"
        db.commit()
    assert session_app["client"].get("/auth/session").status_code == 401


def test_deactivation_invalidates_administrator_session(session_app):
    assert login(session_app).status_code == 200
    with Session(session_app["engine"]) as db:
        user = db.get(
            session_app["user_model"],
            session_app["users"]["super_admin"],
        )
        user.is_active = False
        db.commit()
    assert session_app["client"].get("/auth/session").status_code == 401


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"Origin": "http://untrusted.invalid", "X-CSRF-Token": "invalid"},
        {"Origin": ORIGIN, "X-CSRF-Token": "invalid"},
    ],
)
def test_cookie_mutations_reject_missing_origin_or_csrf(session_app, headers):
    assert login(session_app).status_code == 200
    with Session(session_app["engine"]) as db:
        original_hash = db.get(
            session_app["user_model"],
            session_app["users"]["super_admin"],
        ).hashed_password
    response = session_app["client"].post(
        "/auth/change-password",
        headers=headers,
        json={"current_password": PASSWORD, "new_password": "replacement-password"},
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "CSRF validation failed"}
    with Session(session_app["engine"]) as db:
        assert db.get(
            session_app["user_model"],
            session_app["users"]["super_admin"],
        ).hashed_password == original_hash


def test_valid_csrf_allows_cookie_authenticated_mutation(session_app):
    csrf_token = login(session_app).json()["csrf_token"]
    response = session_app["client"].post(
        "/auth/change-password",
        headers={"Origin": ORIGIN, "X-CSRF-Token": csrf_token},
        json={"current_password": PASSWORD, "new_password": "replacement-password"},
    )
    assert response.status_code == 200


def test_invalid_explicit_bearer_does_not_fall_back_to_cookie(session_app):
    assert login(session_app).status_code == 200
    response = session_app["client"].get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401


def test_existing_bearer_login_and_authentication_remain_supported(session_app):
    login_response = session_app["client"].post(
        "/auth/login",
        data={"username": "super_admin@example.com", "password": PASSWORD},
    )
    assert login_response.status_code == 200
    response = session_app["client"].get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {login_response.json()['access_token']}"
        },
    )
    assert response.status_code == 200
    assert response.json()["role"] == "super_admin"


def test_session_login_enforces_origin_activity_and_administrator_role(session_app):
    assert login(session_app, origin="http://untrusted.invalid").status_code == 403
    assert login(session_app, role="inactive").status_code == 401
    assert login(session_app, role="student").status_code == 403
    assert login(session_app, role="department_admin").status_code == 200
    with Session(session_app["engine"]) as db:
        assert db.scalar(
            select(func.count()).select_from(session_app["session_model"])
        ) == 1
