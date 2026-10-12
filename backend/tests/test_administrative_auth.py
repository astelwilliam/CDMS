from datetime import timedelta
import re

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool


# Explicit inventory makes missing registrations visible rather than silently
# reducing coverage when a router disappears.
ROUTERS = [
    ("college", "colleges", "college_id"),
    ("department", "departments", "department_id"),
    ("faculty_member", "faculty_members", "faculty_member_id"),
    ("announcement", "announcements", "announcement_id"),
    ("event", "events", "event_id"),
    ("academic_resource", "academic_resources", "resource_id"),
    ("timetable", "timetables", "timetable_id"),
    ("gallery_album", "gallery_albums", "album_id"),
    ("gallery_image", "gallery_images", "image_id"),
    ("academic_calendar", "academic_calendars", "calendar_id"),
    ("help_center_article", "help_center_articles", "article_id"),
    ("setting", "settings", "setting_id"),
    ("audit_log", "audit_logs", "log_id"),
    ("role", "roles", "role_id"),
    ("permission", "permissions", "permission_id"),
    ("department_administrator", "department_administrators", "admin_id"),
    ("super_administrator", "super_administrators", "admin_id"),
]
OPERATIONS = [
    (method, path)
    for module, prefix, parameter in ROUTERS
    for method, path in (
        [("GET", f"/{prefix}/"), ("GET", f"/{prefix}/{{{parameter}}}")]
        + ([] if module == "audit_log" else [
            ("POST", f"/{prefix}/"),
            ("PUT", f"/{prefix}/{{{parameter}}}"),
            ("DELETE", f"/{prefix}/{{{parameter}}}"),
        ])
    )
]


@pytest.fixture(scope="module")
def boundary():
    with pytest.MonkeyPatch.context() as patch:
        patch.setenv("DATABASE_URL", "sqlite://")
        patch.setenv("SECRET_KEY", "isolated-boundary-test-key")
        patch.setenv("DEBUG", "false")
        patch.setenv("BACKEND_CORS_ORIGINS", "[]")

        from app.main import app
        from app.api.deps.database import get_db
        from app.core.security import create_access_token, hash_password
        from app.db.session import Base
        from app.models.user import User

        engine = create_engine(
            "sqlite://", connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(engine)
        with Session(engine) as db:
            active = User(
                email="boundary@example.com", hashed_password=hash_password("test-password"),
                role="super_admin", is_active=True,
            )
            inactive = User(
                email="inactive-boundary@example.com", hashed_password=active.hashed_password,
                role="super_admin", is_active=False,
            )
            department = User(
                email="department-boundary@example.com", hashed_password=active.hashed_password,
                role="department_admin", is_active=True,
            )
            unknown = User(
                email="unknown-boundary@example.com", hashed_password=active.hashed_password,
                role="unrecognized_role", is_active=True,
            )
            db.add_all([active, inactive, department, unknown])
            db.commit()
            tokens = {
                "valid": create_access_token({"sub": active.id, "role": active.role}),
                "department": create_access_token({"sub": department.id, "role": department.role}),
                "unknown": create_access_token({"sub": unknown.id, "role": "super_admin"}),
                "inactive": create_access_token({"sub": inactive.id}),
                "expired": create_access_token(
                    {"sub": active.id}, expires_delta=timedelta(minutes=-1)
                ),
                "invalid": "not-a-valid-jwt",
            }

        def isolated_db():
            with Session(engine) as db:
                yield db

        previous_overrides = app.dependency_overrides.copy()
        app.dependency_overrides[get_db] = isolated_db
        try:
            with TestClient(app) as client:
                yield client, tokens, app, engine
        finally:
            app.dependency_overrides.clear()
            app.dependency_overrides.update(previous_overrides)
            engine.dispose()


def test_inventory_matches_registered_business_operations(boundary):
    _, _, app, _ = boundary
    actual = {
        (method, route.path)
        for route in app.routes
        if isinstance(route, APIRoute)
        and route.path != "/health" and not route.path.startswith("/auth/")
        for method in route.methods
    }
    assert actual == set(OPERATIONS)


@pytest.mark.parametrize("method,path", OPERATIONS)
@pytest.mark.parametrize("credential", ["missing", "invalid", "expired", "inactive"])
def test_every_business_operation_rejects_unauthorized_requests(
    boundary, method, path, credential
):
    client, tokens, _, _ = boundary
    headers = {} if credential == "missing" else {
        "Authorization": f"Bearer {tokens[credential]}"
    }
    url = re.sub(r"\{[^}]+\}", "missing-record", path)
    response = client.request(method, url, headers=headers, json={})
    # Empty write bodies must still fail authentication, not reach validation
    # (422), record lookup (404), or persistence.
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize("module,prefix,parameter", ROUTERS)
def test_super_admin_can_list_each_business_router(boundary, module, prefix, parameter):
    client, tokens, _, _ = boundary
    response = client.get(
        f"/{prefix}/", headers={"Authorization": f"Bearer {tokens['valid']}"}
    )
    assert response.status_code == 200
    assert response.json() == []


def test_authenticated_representative_crud(boundary):
    client, tokens, _, _ = boundary
    headers = {"Authorization": f"Bearer {tokens['valid']}"}
    response = client.post("/colleges/", headers=headers, json={"name": "Boundary college"})
    assert response.status_code == 201
    path = f"/colleges/{response.json()['id']}"
    assert client.get(path, headers=headers).status_code == 200
    response = client.put(path, headers=headers, json={"name": "Updated boundary college"})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated boundary college"
    assert client.delete(path, headers=headers).status_code == 204
    assert client.get(path, headers=headers).status_code == 404


def test_login_remains_public(boundary):
    client, _, _, _ = boundary
    response = client.post(
        "/auth/login",
        data={"username": "boundary@example.com", "password": "test-password"},
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


@pytest.mark.parametrize("path", [
    "/health", "/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"
])
def test_explicit_public_endpoints_remain_accessible(boundary, path):
    client, _, _, _ = boundary
    assert client.get(path).status_code == 200


@pytest.mark.parametrize("method,path", OPERATIONS)
@pytest.mark.parametrize("credential", ["department", "unknown"])
def test_non_super_admin_rejected_on_every_business_operation(boundary, method, path, credential):
    client, tokens, _, _ = boundary
    response = client.request(
        method, re.sub(r"\{[^}]+\}", "missing-record", path),
        headers={"Authorization": f"Bearer {tokens[credential]}"}, json={},
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Access denied. Required role: super_admin"}


@pytest.mark.parametrize("role", ["department_admin", "unrecognized_role", "SUPER_ADMIN", ""])
def test_database_role_changes_override_stale_super_admin_claim(boundary, role):
    from app.core.security import decode_access_token
    from app.models.user import User

    client, tokens, _, engine = boundary
    token = tokens["valid"]
    user_id = decode_access_token(token)["sub"]
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get("/colleges/", headers=headers).status_code == 200
    try:
        with Session(engine) as db:
            db.get(User, user_id).role = role
            db.commit()
        assert client.get("/colleges/", headers=headers).status_code == 403
    finally:
        with Session(engine) as db:
            db.get(User, user_id).role = "super_admin"
            db.commit()
    assert client.get("/colleges/", headers=headers).status_code == 200


def test_database_promotion_overrides_stale_department_claim(boundary):
    from app.core.security import decode_access_token
    from app.models.user import User

    client, tokens, _, engine = boundary
    token = tokens["department"]
    user_id = decode_access_token(token)["sub"]
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get("/colleges/", headers=headers).status_code == 403
    try:
        with Session(engine) as db:
            db.get(User, user_id).role = "super_admin"
            db.commit()
        assert client.get("/colleges/", headers=headers).status_code == 200
    finally:
        with Session(engine) as db:
            db.get(User, user_id).role = "department_admin"
            db.commit()
    assert client.get("/colleges/", headers=headers).status_code == 403


def test_department_admin_retains_own_profile_and_password_change(boundary):
    from app.core.security import decode_access_token, verify_password
    from app.models.user import User

    client, tokens, _, engine = boundary
    headers = {"Authorization": f"Bearer {tokens['department']}"}
    user_id = decode_access_token(tokens["department"])["sub"]
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == user_id
    assert response.json()["role"] == "department_admin"
    with Session(engine) as db:
        original_hash = db.get(User, user_id).hashed_password
        admin_id = decode_access_token(tokens["valid"])["sub"]
        admin_hash = db.get(User, admin_id).hashed_password
    try:
        response = client.post(
            "/auth/change-password", headers=headers,
            json={"current_password": "test-password", "new_password": "new-department-password"},
        )
        assert response.status_code == 200
        assert response.json() == {"message": "Password changed successfully"}
        with Session(engine) as db:
            new_hash = db.get(User, user_id).hashed_password
            assert verify_password("new-department-password", new_hash)
            assert not verify_password("test-password", new_hash)
            assert db.get(User, admin_id).hashed_password == admin_hash
    finally:
        with Session(engine) as db:
            db.get(User, user_id).hashed_password = original_hash
            db.commit()
