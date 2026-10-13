from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool


@pytest.fixture
def faculty_mutation_boundary(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite://")
    monkeypatch.setenv("SECRET_KEY", "privileged-faculty-mutation-key")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("BACKEND_CORS_ORIGINS", "[]")

    import app.models  # noqa: F401 - register complete relationship metadata
    from app.api.deps.database import get_db
    from app.core.security import create_access_token
    from app.db.session import Base
    from app.main import app
    from app.models.college import College
    from app.models.department import Department
    from app.models.faculty_member import FacultyMember
    from app.models.user import User

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        college = College(name="Privileged Faculty College")
        users = {
            "super": User(
                email="privileged-faculty-super@example.com",
                hashed_password="unused",
                role="super_admin",
                is_active=True,
            ),
            "department": User(
                email="privileged-faculty-department@example.com",
                hashed_password="unused",
                role="department_admin",
                is_active=True,
            ),
        }
        db.add_all([college, *users.values()])
        db.flush()
        departments = {
            "active": Department(name="Active", college_id=college.id),
            "deleted": Department(
                name="Deleted",
                college_id=college.id,
                deleted_at=datetime.now(timezone.utc),
            ),
        }
        db.add_all(departments.values())
        db.flush()
        faculty = {
            "active": FacultyMember(
                name="Original Faculty", department_id=departments["active"].id
            ),
            "deleted": FacultyMember(
                name="Deleted Faculty",
                department_id=departments["active"].id,
                deleted_at=datetime.now(timezone.utc),
            ),
            "deleted_parent": FacultyMember(
                name="Deleted Parent Faculty",
                department_id=departments["deleted"].id,
            ),
        }
        db.add_all(faculty.values())
        db.commit()
        ids = {
            "users": {name: user.id for name, user in users.items()},
            "departments": {
                name: department.id for name, department in departments.items()
            },
            "faculty": {name: member.id for name, member in faculty.items()},
        }
        tokens = {
            name: create_access_token({"sub": user.id, "role": user.role})
            for name, user in users.items()
        }

    def isolated_db():
        with Session(engine) as db:
            yield db

    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = isolated_db
    try:
        with TestClient(app) as client:
            yield client, engine, ids, tokens
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)
        engine.dispose()


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_create_service_flushes_and_commits_exactly_once():
    from app.models.department import Department
    from app.models.user import User
    from app.services.privileged_faculty_mutation import (
        create_faculty_as_super_admin,
    )

    db = MagicMock(spec=Session)
    db.scalar.side_effect = [
        User(id="super-id", role="super_admin", is_active=True),
        Department(id="department-id", college_id="college-id", name="Department"),
    ]

    faculty = create_faculty_as_super_admin(
        db,
        "super-id",
        "department-id",
        {"name": "Created Faculty"},
    )

    assert faculty.department_id == "department-id"
    db.add.assert_called_once_with(faculty)
    db.flush.assert_called_once_with()
    db.commit.assert_called_once_with()
    db.refresh.assert_called_once_with(faculty)
    db.rollback.assert_not_called()


def test_super_admin_can_create_update_and_soft_delete(faculty_mutation_boundary):
    from app.models.faculty_member import FacultyMember

    client, engine, ids, tokens = faculty_mutation_boundary
    headers = auth(tokens["super"])
    response = client.post(
        "/faculty_members/",
        headers=headers,
        json={
            "department_id": ids["departments"]["active"],
            "name": "Created Faculty",
        },
    )
    assert response.status_code == 201
    faculty_id = response.json()["id"]

    response = client.put(
        f"/faculty_members/{faculty_id}",
        headers=headers,
        json={"name": "Updated Faculty", "title": "Professor"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Faculty"

    assert client.delete(
        f"/faculty_members/{faculty_id}", headers=headers
    ).status_code == 204
    with Session(engine) as db:
        faculty = db.get(FacultyMember, faculty_id)
        assert faculty is not None
        assert faculty.deleted_at is not None
        assert faculty.department_id == ids["departments"]["active"]


@pytest.mark.parametrize("department", ["deleted", "missing"])
def test_create_rejects_invalid_or_deleted_department(
    faculty_mutation_boundary, department
):
    from app.models.faculty_member import FacultyMember

    client, engine, ids, tokens = faculty_mutation_boundary
    department_id = (
        ids["departments"]["deleted"]
        if department == "deleted"
        else "missing-department"
    )
    response = client.post(
        "/faculty_members/",
        headers=auth(tokens["super"]),
        json={"department_id": department_id, "name": "Must Not Exist"},
    )
    assert response.status_code == 404
    with Session(engine) as db:
        assert not db.query(FacultyMember).filter_by(name="Must Not Exist").first()


@pytest.mark.parametrize("field", ["department_id", "id", "deleted_at"])
def test_update_rejects_ownership_and_system_field_tampering(
    faculty_mutation_boundary, field
):
    client, _, ids, tokens = faculty_mutation_boundary
    response = client.put(
        f"/faculty_members/{ids['faculty']['active']}",
        headers=auth(tokens["super"]),
        json={field: "untrusted", "name": "Tampered"},
    )
    assert response.status_code == 422


@pytest.mark.parametrize("field", ["id", "deleted_at"])
def test_create_rejects_system_field_tampering(
    faculty_mutation_boundary, field
):
    client, _, ids, tokens = faculty_mutation_boundary
    response = client.post(
        "/faculty_members/",
        headers=auth(tokens["super"]),
        json={
            "department_id": ids["departments"]["active"],
            "name": "Tampered",
            field: "untrusted",
        },
    )
    assert response.status_code == 422


@pytest.mark.parametrize("operation", ["update", "delete"])
@pytest.mark.parametrize("target", ["deleted", "deleted_parent"])
def test_update_and_delete_reject_deleted_targets_or_parents(
    faculty_mutation_boundary, operation, target
):
    client, _, ids, tokens = faculty_mutation_boundary
    path = f"/faculty_members/{ids['faculty'][target]}"
    if operation == "update":
        response = client.put(
            path, headers=auth(tokens["super"]), json={"name": "Rejected"}
        )
    else:
        response = client.delete(path, headers=auth(tokens["super"]),)
    assert response.status_code == 404
    assert response.json() == {"detail": "Faculty member not found"}


def test_failed_update_rolls_back_the_staged_change(
    faculty_mutation_boundary, monkeypatch
):
    from app.models.faculty_member import FacultyMember
    from app.repositories.faculty_member_repository import FacultyMemberRepository
    from app.services.privileged_faculty_mutation import update_faculty_as_super_admin

    _, engine, ids, _ = faculty_mutation_boundary

    def fail_after_change(self, faculty, values):
        faculty.name = values["name"]
        self.db.flush()
        raise RuntimeError("injected failure")

    monkeypatch.setattr(
        FacultyMemberRepository, "update_for_scoped_write", fail_after_change
    )
    with Session(engine) as db:
        with pytest.raises(RuntimeError, match="injected failure"):
            update_faculty_as_super_admin(
                db,
                ids["users"]["super"],
                ids["faculty"]["active"],
                {"name": "Must Roll Back"},
            )
        assert not db.in_transaction()

    with Session(engine) as db:
        assert (
            db.get(FacultyMember, ids["faculty"]["active"]).name
            == "Original Faculty"
        )


@pytest.mark.parametrize(
    "method,path,payload",
    [
        ("POST", "/faculty_members/", {"name": "Denied", "department_id": "x"}),
        ("PUT", "/faculty_members/x", {"name": "Denied"}),
        ("DELETE", "/faculty_members/x", None),
    ],
)
def test_department_admin_writes_remain_forbidden(
    faculty_mutation_boundary, method, path, payload
):
    client, _, _, tokens = faculty_mutation_boundary
    response = client.request(
        method,
        path,
        headers=auth(tokens["department"]),
        json=payload,
    )
    assert response.status_code == 403

