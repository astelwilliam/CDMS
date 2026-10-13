from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool


@pytest.fixture
def scoped_create_boundary(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite://")
    monkeypatch.setenv("SECRET_KEY", "scoped-faculty-create-key")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("BACKEND_CORS_ORIGINS", "[]")

    import app.models  # noqa: F401 - register complete relationship metadata
    from app.api.deps.database import get_db
    from app.core.security import create_access_token
    from app.db.session import Base
    from app.main import app
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
        role = Role(name="scoped-faculty-create-role")
        colleges = {
            "own": College(name="Scoped Faculty College"),
            "other": College(name="Other Scoped Faculty College"),
        }
        users = {
            "super": User(
                email="scoped-create-super@example.com",
                hashed_password="unused",
                role="super_admin",
                is_active=True,
            ),
            "department": User(
                email="scoped-create-department@example.com",
                hashed_password="unused",
                role="department_admin",
                is_active=True,
            ),
            "unlinked": User(
                email="scoped-creator@example.com",
                hashed_password="unused",
                role="department_admin",
                is_active=True,
            ),
            "empty": User(
                email="scoped-create-empty@example.com",
                hashed_password="unused",
                role="department_admin",
                is_active=True,
            ),
            "inactive": User(
                email="scoped-create-inactive@example.com",
                hashed_password="unused",
                role="department_admin",
                is_active=False,
            ),
            "changed": User(
                email="scoped-create-changed@example.com",
                hashed_password="unused",
                role="department_admin",
                is_active=True,
            ),
        }
        db.add_all([role, *colleges.values(), *users.values()])
        db.flush()
        departments = {
            "first": Department(name="First", college_id=colleges["own"].id),
            "second": Department(name="Second", college_id=colleges["own"].id),
            "outside": Department(name="Outside", college_id=colleges["own"].id),
            "other_college": Department(
                name="Other College", college_id=colleges["other"].id
            ),
            "deleted": Department(
                name="Deleted",
                college_id=colleges["own"].id,
                deleted_at=datetime.now(timezone.utc),
            ),
        }
        db.add_all(departments.values())
        db.flush()
        administrators = {
            "department": DepartmentAdministrator(
                name="Scoped Creator",
                email="scoped-creator@example.com",
                role_id=role.id,
                user_id=users["department"].id,
            ),
            "empty": DepartmentAdministrator(
                name="Empty Creator",
                email="empty-creator@example.com",
                role_id=role.id,
                user_id=users["empty"].id,
            ),
            "inactive": DepartmentAdministrator(
                name="Inactive Creator",
                email="inactive-creator@example.com",
                role_id=role.id,
                user_id=users["inactive"].id,
            ),
            "changed": DepartmentAdministrator(
                name="Changed Creator",
                email="changed-creator@example.com",
                role_id=role.id,
                user_id=users["changed"].id,
            ),
        }
        db.add_all(administrators.values())
        db.flush()
        db.execute(
            department_administrator_departments.insert(),
            [
                {
                    "department_administrator_id": administrators["department"].id,
                    "department_id": departments[name].id,
                }
                for name in ("first", "second", "deleted")
            ]
            + [
                {
                    "department_administrator_id": administrators[name].id,
                    "department_id": departments["first"].id,
                }
                for name in ("inactive", "changed")
            ],
        )
        db.commit()
        tokens = {
            name: create_access_token(
                {
                    "sub": user.id,
                    "role": "super_admin" if name == "department" else user.role,
                    "department_id": departments["other_college"].id,
                }
            )
            for name, user in users.items()
        }
        users["changed"].role = "unknown_role"
        db.commit()
        ids = {
            "administrator": administrators["department"].id,
            "departments": {
                name: department.id for name, department in departments.items()
            },
        }

    def isolated_db():
        with Session(engine) as db:
            yield db

    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = isolated_db
    try:
        with TestClient(app) as client:
            yield client, engine, ids, tokens, department_administrator_departments
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)
        engine.dispose()


def auth(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.parametrize("department", ["first", "second"])
def test_department_admin_creates_in_each_assigned_department(
    scoped_create_boundary, department
):
    client, engine, ids, tokens, _ = scoped_create_boundary
    response = client.post(
        "/faculty_members/",
        headers=auth(tokens["department"]),
        json={
            "department_id": ids["departments"][department],
            "name": f"Assigned {department}",
        },
    )
    assert response.status_code == 201
    assert response.json()["department_id"] == ids["departments"][department]

    from app.models.faculty_member import FacultyMember

    with Session(engine) as db:
        faculty = db.get(FacultyMember, response.json()["id"])
        assert faculty is not None
        assert faculty.department_id == ids["departments"][department]


@pytest.mark.parametrize(
    "department", ["outside", "other_college", "deleted"]
)
def test_unauthorized_or_deleted_department_is_hidden(
    scoped_create_boundary, department
):
    client, engine, ids, tokens, _ = scoped_create_boundary
    response = client.post(
        "/faculty_members/",
        headers=auth(tokens["department"]),
        json={
            "department_id": ids["departments"][department],
            "name": "Must Not Exist",
        },
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Department not found"}

    from app.models.faculty_member import FacultyMember

    with Session(engine) as db:
        assert db.scalar(
            select(FacultyMember.id).where(FacultyMember.name == "Must Not Exist")
        ) is None


@pytest.mark.parametrize("credential", ["unlinked", "changed"])
def test_invalid_department_identity_is_denied(
    scoped_create_boundary, credential
):
    client, _, ids, tokens, _ = scoped_create_boundary
    response = client.post(
        "/faculty_members/",
        headers=auth(tokens[credential]),
        json={
            "department_id": ids["departments"]["first"],
            "name": "Denied",
        },
    )
    assert response.status_code == 403
    assert response.json() == {
        "detail": "Department administrator access unavailable"
    }


def test_linked_admin_without_assignments_cannot_create(scoped_create_boundary):
    client, _, ids, tokens, _ = scoped_create_boundary
    response = client.post(
        "/faculty_members/",
        headers=auth(tokens["empty"]),
        json={
            "department_id": ids["departments"]["first"],
            "name": "Denied",
        },
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Department not found"}


def test_inactive_department_admin_is_rejected(scoped_create_boundary):
    client, _, ids, tokens, _ = scoped_create_boundary
    response = client.post(
        "/faculty_members/",
        headers=auth(tokens["inactive"]),
        json={
            "department_id": ids["departments"]["first"],
            "name": "Denied",
        },
    )
    assert response.status_code == 401


def test_revoked_assignment_applies_before_create(scoped_create_boundary):
    client, engine, ids, tokens, assignment_table = scoped_create_boundary
    with Session(engine) as db:
        db.execute(
            delete(assignment_table).where(
                assignment_table.c.department_administrator_id
                == ids["administrator"],
                assignment_table.c.department_id
                == ids["departments"]["first"],
            )
        )
        db.commit()

    response = client.post(
        "/faculty_members/",
        headers=auth(tokens["department"]),
        json={
            "department_id": ids["departments"]["first"],
            "name": "Revoked",
        },
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Department not found"}


def test_cross_college_assignment_state_fails_closed(scoped_create_boundary):
    client, engine, ids, tokens, assignment_table = scoped_create_boundary
    with Session(engine) as db:
        db.execute(
            assignment_table.insert(),
            {
                "department_administrator_id": ids["administrator"],
                "department_id": ids["departments"]["other_college"],
            },
        )
        db.commit()

    response = client.post(
        "/faculty_members/",
        headers=auth(tokens["department"]),
        json={
            "department_id": ids["departments"]["first"],
            "name": "Cross College Denied",
        },
    )
    assert response.status_code == 403
    assert response.json() == {
        "detail": "Department administrator access unavailable"
    }


@pytest.mark.parametrize("field", ["id", "deleted_at"])
def test_department_admin_cannot_set_system_fields(
    scoped_create_boundary, field
):
    client, _, ids, tokens, _ = scoped_create_boundary
    response = client.post(
        "/faculty_members/",
        headers=auth(tokens["department"]),
        json={
            "department_id": ids["departments"]["first"],
            "name": "Tampered",
            field: "untrusted",
        },
    )
    assert response.status_code == 422


def test_super_admin_create_remains_available(scoped_create_boundary):
    client, _, ids, tokens, _ = scoped_create_boundary
    response = client.post(
        "/faculty_members/",
        headers=auth(tokens["super"]),
        json={
            "department_id": ids["departments"]["outside"],
            "name": "Super Created",
        },
    )
    assert response.status_code == 201


def test_department_create_service_rolls_back_database_failures(monkeypatch):
    from app.repositories.faculty_member_repository import FacultyMemberRepository
    from app.services import privileged_faculty_mutation as mutation_service

    db = MagicMock(spec=Session)
    monkeypatch.setattr(
        mutation_service,
        "lock_department_write_access",
        lambda *args: SimpleNamespace(
            department=SimpleNamespace(id="department-id")
        ),
    )
    monkeypatch.setattr(
        FacultyMemberRepository,
        "add_for_scoped_write",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("db failure")),
    )

    with pytest.raises(RuntimeError, match="db failure"):
        mutation_service.create_faculty_as_department_admin(
            db,
            "user-id",
            "department-id",
            {"name": "Must Roll Back"},
        )

    db.rollback.assert_called_once_with()
    db.commit.assert_not_called()


@pytest.mark.parametrize("method", ["PUT", "DELETE"])
def test_department_admin_update_and_delete_remain_forbidden(
    scoped_create_boundary, method
):
    client, _, _, tokens, _ = scoped_create_boundary
    response = client.request(
        method,
        "/faculty_members/missing",
        headers=auth(tokens["department"]),
        json={"name": "Denied"} if method == "PUT" else None,
    )
    assert response.status_code == 403
