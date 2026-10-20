"""API pagination and scope checks using an isolated in-memory database."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool


@pytest.fixture(scope="module")
def pagination_api():
    with pytest.MonkeyPatch.context() as patch:
        patch.setenv("DATABASE_URL", "sqlite://")
        patch.setenv("SECRET_KEY", "isolated-pagination-test-key")
        patch.setenv("DEBUG", "false")
        patch.setenv("BACKEND_CORS_ORIGINS", "[]")

        from app.api.deps.database import get_db
        from app.core.security import create_access_token
        from app.db.session import Base
        from app.main import app
        from app.models.association_tables import department_administrator_departments
        from app.models.college import College
        from app.models.department import Department
        from app.models.department_administrator import DepartmentAdministrator
        from app.models.faculty_member import FacultyMember
        from app.models.role import Role
        from app.models.user import User

        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(engine)

        with Session(engine) as db:
            role = Role(name="pagination-role")
            super_user = User(
                email="pagination-super@example.com",
                hashed_password="unused",
                role="super_admin",
                is_active=True,
            )
            department_user = User(
                email="pagination-department@example.com",
                hashed_password="unused",
                role="department_admin",
                is_active=True,
            )
            db.add_all([role, super_user, department_user])
            db.flush()

            # Reverse insertion order exposes pagination that follows row order.
            colleges = [
                College(id=f"pagination-college-{number:03d}", name=f"College {number:03d}")
                for number in reversed(range(105))
            ]
            db.add_all(colleges)
            db.flush()
            departments = [
                Department(
                    id=f"pagination-department-{number:03d}",
                    name=f"Department {number:03d}",
                    college_id="pagination-college-000",
                )
                for number in reversed(range(105))
            ]
            db.add_all(departments)
            db.flush()
            db.add_all(
                FacultyMember(
                    id=f"pagination-faculty-{number:03d}",
                    name=f"Faculty {number:03d}",
                    department_id=f"pagination-department-{number:03d}",
                )
                for number in reversed(range(105))
            )

            administrator = DepartmentAdministrator(
                name="Pagination Administrator",
                email="pagination-administrator@example.com",
                role_id=role.id,
                user_id=department_user.id,
            )
            db.add(administrator)
            db.flush()
            assigned_numbers = (1, 51, 101)
            db.execute(
                department_administrator_departments.insert(),
                [
                    {
                        "department_administrator_id": administrator.id,
                        "department_id": f"pagination-department-{number:03d}",
                    }
                    for number in assigned_numbers
                ],
            )
            db.commit()

            tokens = {
                # Deliberately wrong JWT roles: authorization uses current DB state.
                "super": create_access_token(
                    {"sub": super_user.id, "role": "department_admin"}
                ),
                "department": create_access_token(
                    {"sub": department_user.id, "role": "super_admin"}
                ),
            }

        def isolated_db():
            with Session(engine) as db:
                yield db

        previous_overrides = app.dependency_overrides.copy()
        app.dependency_overrides[get_db] = isolated_db
        try:
            with TestClient(app) as client:
                yield client, tokens, assigned_numbers
        finally:
            app.dependency_overrides.clear()
            app.dependency_overrides.update(previous_overrides)
            engine.dispose()


def auth(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.parametrize(
    "path,prefix",
    [
        ("/colleges/", "pagination-college"),
        ("/departments/", "pagination-department"),
        ("/faculty_members/", "pagination-faculty"),
    ],
)
def test_super_admin_pages_are_complete_and_ordered(pagination_api, path, prefix):
    client, tokens, _ = pagination_api
    page_size = 40
    observed = []
    for skip in (0, 40, 80, 120):
        response = client.get(
            path,
            params={"skip": skip, "limit": page_size},
            headers=auth(tokens["super"]),
        )
        assert response.status_code == 200
        observed.extend(item["id"] for item in response.json())

    expected = [f"{prefix}-{number:03d}" for number in range(105)]
    assert observed == expected
    assert len(observed) == len(set(observed))


@pytest.mark.parametrize(
    "path,prefix",
    [
        ("/departments/", "pagination-department"),
        ("/faculty_members/", "pagination-faculty"),
    ],
)
def test_department_admin_pages_stay_scoped(pagination_api, path, prefix):
    client, tokens, assigned_numbers = pagination_api
    observed = []
    for skip in range(4):
        response = client.get(
            path,
            params={"skip": skip, "limit": 1},
            headers=auth(tokens["department"]),
        )
        assert response.status_code == 200
        observed.extend(item["id"] for item in response.json())

    assert observed == [f"{prefix}-{number:03d}" for number in assigned_numbers]


@pytest.mark.parametrize("path", ["/colleges/", "/departments/", "/faculty_members/"])
def test_paginated_lists_still_require_authentication(pagination_api, path):
    client, _, _ = pagination_api
    assert client.get(path, params={"skip": 0, "limit": 1}).status_code == 401


def test_department_admin_cannot_read_colleges(pagination_api):
    client, tokens, _ = pagination_api
    response = client.get(
        "/colleges/", params={"skip": 0, "limit": 1}, headers=auth(tokens["department"])
    )
    assert response.status_code == 403
