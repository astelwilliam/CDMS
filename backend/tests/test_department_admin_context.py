from datetime import datetime, timezone

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete, update
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool


PASSWORD_HASH = "unused-test-hash"
DENIED = {"detail": "Department administrator access unavailable"}


@pytest.fixture
def identity_context(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite://")
    monkeypatch.setenv("SECRET_KEY", "isolated-department-context-test-key")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("BACKEND_CORS_ORIGINS", "[]")

    from app.api.deps.auth import (
        DepartmentAdministratorContext,
        get_department_administrator_context,
    )
    from app.api.deps.database import get_db
    from app.core.security import create_access_token
    from app.db.session import Base
    from app.models.association_tables import department_administrator_departments
    from app.models.college import College
    from app.models.department import Department
    from app.models.department_administrator import DepartmentAdministrator
    from app.models.role import Role
    from app.models.user import User

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        role = Role(name="context-role")
        college = College(name="Context College")
        other_college = College(name="Other Context College")
        db.add_all([role, college, other_college])
        db.flush()

        departments = {
            "first": Department(name="First", college_id=college.id),
            "second": Department(name="Second", college_id=college.id),
            "deleted": Department(
                name="Deleted",
                college_id=college.id,
                deleted_at=datetime.now(timezone.utc),
            ),
            "other_college": Department(name="Other", college_id=other_college.id),
        }
        users = {
            "linked": User(
                email="linked-context@example.com",
                hashed_password=PASSWORD_HASH,
                role="department_admin",
                is_active=True,
            ),
            "unlinked": User(
                email="matching-context@example.com",
                hashed_password=PASSWORD_HASH,
                role="department_admin",
                is_active=True,
            ),
            "no_assignments": User(
                email="empty-context@example.com",
                hashed_password=PASSWORD_HASH,
                role="department_admin",
                is_active=True,
            ),
            "inactive": User(
                email="inactive-context@example.com",
                hashed_password=PASSWORD_HASH,
                role="department_admin",
                is_active=False,
            ),
            "unknown": User(
                email="unknown-context@example.com",
                hashed_password=PASSWORD_HASH,
                role="unknown_role",
                is_active=True,
            ),
            "super": User(
                email="super-context@example.com",
                hashed_password=PASSWORD_HASH,
                role="super_admin",
                is_active=True,
            ),
        }
        db.add_all([*departments.values(), *users.values()])
        db.flush()

        administrators = {
            "linked": DepartmentAdministrator(
                name="Linked Admin",
                email="unrelated-admin-email@example.com",
                role_id=role.id,
                user_id=users["linked"].id,
            ),
            "email_only": DepartmentAdministrator(
                name="Email Match Only",
                email=users["unlinked"].email,
                role_id=role.id,
                user_id=None,
            ),
            "no_assignments": DepartmentAdministrator(
                name="No Assignments",
                email="empty-admin@example.com",
                role_id=role.id,
                user_id=users["no_assignments"].id,
            ),
            "inactive": DepartmentAdministrator(
                name="Inactive",
                email="inactive-admin@example.com",
                role_id=role.id,
                user_id=users["inactive"].id,
            ),
            "unknown": DepartmentAdministrator(
                name="Unknown",
                email="unknown-admin@example.com",
                role_id=role.id,
                user_id=users["unknown"].id,
            ),
        }
        db.add_all(administrators.values())
        db.flush()
        db.execute(
            department_administrator_departments.insert(),
            [
                {
                    "department_administrator_id": administrators["linked"].id,
                    "department_id": departments[name].id,
                }
                for name in ("first", "second", "deleted")
            ]
            + [
                {
                    "department_administrator_id": administrators[key].id,
                    "department_id": departments["first"].id,
                }
                for key in ("inactive", "unknown")
            ],
        )
        db.commit()

        ids = {
            "users": {key: value.id for key, value in users.items()},
            "administrators": {
                key: value.id for key, value in administrators.items()
            },
            "departments": {key: value.id for key, value in departments.items()},
            "college": college.id,
        }
        tokens = {
            key: create_access_token(
                {
                    "sub": user_id,
                    "role": "super_admin" if key in ("linked", "unknown") else "department_admin",
                }
            )
            for key, user_id in ids["users"].items()
        }
        tokens["missing_user"] = create_access_token(
            {"sub": "missing-context-user", "role": "department_admin"}
        )
        tokens["invalid"] = "not-a-valid-jwt"

    def isolated_db():
        with Session(engine) as db:
            yield db

    app = FastAPI()

    @app.get("/context")
    def context_endpoint(
        context: DepartmentAdministratorContext = Depends(
            get_department_administrator_context
        ),
    ):
        return {
            "user_id": context.user.id,
            "administrator_id": context.administrator_id,
            "department_ids": sorted(context.department_ids),
            "college_id": context.college_id,
        }

    app.dependency_overrides[get_db] = isolated_db
    try:
        with TestClient(app) as client:
            yield {
                "client": client,
                "engine": engine,
                "ids": ids,
                "tokens": tokens,
                "tables": {
                    "assignment": department_administrator_departments,
                    "administrator": DepartmentAdministrator,
                    "user": User,
                },
            }
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def request_context(context, identity):
    return context["client"].get(
        "/context",
        headers={"Authorization": f"Bearer {context['tokens'][identity]}"},
    )


def assert_forbidden(response):
    assert response.status_code == 403
    assert response.json() == DENIED


def test_resolves_linked_administrator_and_multiple_active_assignments(identity_context):
    response = request_context(identity_context, "linked")
    assert response.status_code == 200
    assert response.json() == {
        "user_id": identity_context["ids"]["users"]["linked"],
        "administrator_id": identity_context["ids"]["administrators"]["linked"],
        "department_ids": sorted(
            [
                identity_context["ids"]["departments"]["first"],
                identity_context["ids"]["departments"]["second"],
            ]
        ),
        "college_id": identity_context["ids"]["college"],
    }


def test_matching_email_without_identity_link_is_forbidden(identity_context):
    assert_forbidden(request_context(identity_context, "unlinked"))


def test_administrator_without_assignments_is_forbidden(identity_context):
    assert_forbidden(request_context(identity_context, "no_assignments"))


def test_inactive_user_is_rejected_before_assignment_resolution(identity_context):
    response = request_context(identity_context, "inactive")
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}


@pytest.mark.parametrize("identity", ["missing_user", "invalid"])
def test_invalid_identity_is_rejected_before_assignment_resolution(
    identity_context, identity
):
    response = request_context(identity_context, identity)
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}


def test_unknown_database_role_overrides_stale_jwt_claim(identity_context):
    assert_forbidden(request_context(identity_context, "unknown"))


def test_super_admin_path_remains_separate(identity_context):
    assert_forbidden(request_context(identity_context, "super"))


def test_database_role_changes_take_effect_on_next_request(identity_context):
    user_model = identity_context["tables"]["user"]
    user_id = identity_context["ids"]["users"]["linked"]
    assert request_context(identity_context, "linked").status_code == 200
    try:
        with Session(identity_context["engine"]) as db:
            db.execute(
                update(user_model)
                .where(user_model.id == user_id)
                .values(role="super_admin")
            )
            db.commit()
        assert_forbidden(request_context(identity_context, "linked"))
    finally:
        with Session(identity_context["engine"]) as db:
            db.execute(
                update(user_model)
                .where(user_model.id == user_id)
                .values(role="department_admin")
            )
            db.commit()
    assert request_context(identity_context, "linked").status_code == 200


def test_removed_identity_link_takes_effect_on_next_request(identity_context):
    administrator_model = identity_context["tables"]["administrator"]
    administrator_id = identity_context["ids"]["administrators"]["linked"]
    try:
        with Session(identity_context["engine"]) as db:
            db.execute(
                update(administrator_model)
                .where(administrator_model.id == administrator_id)
                .values(user_id=None)
            )
            db.commit()
        assert_forbidden(request_context(identity_context, "linked"))
    finally:
        with Session(identity_context["engine"]) as db:
            db.execute(
                update(administrator_model)
                .where(administrator_model.id == administrator_id)
                .values(user_id=identity_context["ids"]["users"]["linked"])
            )
            db.commit()


def test_removed_assignments_take_effect_on_next_request(identity_context):
    assignment = identity_context["tables"]["assignment"]
    administrator_id = identity_context["ids"]["administrators"]["linked"]
    department_ids = [
        identity_context["ids"]["departments"][name]
        for name in ("first", "second", "deleted")
    ]
    try:
        with Session(identity_context["engine"]) as db:
            db.execute(
                delete(assignment).where(
                    assignment.c.department_administrator_id == administrator_id
                )
            )
            db.commit()
        assert_forbidden(request_context(identity_context, "linked"))
    finally:
        with Session(identity_context["engine"]) as db:
            db.execute(
                assignment.insert(),
                [
                    {
                        "department_administrator_id": administrator_id,
                        "department_id": department_id,
                    }
                    for department_id in department_ids
                ],
            )
            db.commit()


def test_cross_college_assignments_fail_closed(identity_context):
    assignment = identity_context["tables"]["assignment"]
    administrator_id = identity_context["ids"]["administrators"]["linked"]
    other_department_id = identity_context["ids"]["departments"]["other_college"]
    try:
        with Session(identity_context["engine"]) as db:
            db.execute(
                assignment.insert().values(
                    department_administrator_id=administrator_id,
                    department_id=other_department_id,
                )
            )
            db.commit()
        assert_forbidden(request_context(identity_context, "linked"))
    finally:
        with Session(identity_context["engine"]) as db:
            db.execute(
                delete(assignment).where(
                    assignment.c.department_administrator_id == administrator_id,
                    assignment.c.department_id == other_department_id,
                )
            )
            db.commit()
