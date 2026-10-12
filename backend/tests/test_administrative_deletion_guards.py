import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool


@pytest.fixture
def deletion_boundary(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite://")
    monkeypatch.setenv("SECRET_KEY", "administrative-deletion-test-key")
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
        role = Role(name="deletion-guard-role")
        college = College(name="Deletion Guard College")
        users = {
            "super": User(
                email="deletion-super@example.com",
                hashed_password="unused",
                role="super_admin",
                is_active=True,
            ),
            "department": User(
                email="deletion-department@example.com",
                hashed_password="unused",
                role="department_admin",
                is_active=True,
            ),
        }
        db.add_all([role, college, *users.values()])
        db.flush()
        department = Department(name="Protected Department", college_id=college.id)
        administrator = DepartmentAdministrator(
            name="Protected Administrator",
            email="protected-administrator@example.com",
            role_id=role.id,
            user_id=users["department"].id,
        )
        db.add_all([department, administrator])
        db.flush()
        faculty = FacultyMember(
            name="Protected Faculty",
            department_id=department.id,
        )
        db.add(faculty)
        db.execute(
            department_administrator_departments.insert(),
            {
                "department_administrator_id": administrator.id,
                "department_id": department.id,
            },
        )
        db.commit()
        ids = {
            "department": department.id,
            "administrator": administrator.id,
            "faculty": faculty.id,
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


@pytest.mark.parametrize(
    "path_key,path_prefix",
    [
        ("department", "/departments"),
        ("administrator", "/department_administrators"),
    ],
)
def test_super_admin_deletion_is_blocked_without_modifying_records(
    deletion_boundary, path_key, path_prefix
):
    from app.models.association_tables import department_administrator_departments
    from app.models.department import Department
    from app.models.department_administrator import DepartmentAdministrator
    from app.models.faculty_member import FacultyMember
    from app.services.administrative_deletion import DELETION_DISABLED_DETAIL

    client, engine, ids, tokens = deletion_boundary
    response = client.delete(
        f"{path_prefix}/{ids[path_key]}",
        headers={"Authorization": f"Bearer {tokens['super']}"},
    )

    assert response.status_code == 409
    assert response.json() == {"detail": DELETION_DISABLED_DETAIL}
    with Session(engine) as db:
        assert db.get(Department, ids["department"]) is not None
        assert db.get(DepartmentAdministrator, ids["administrator"]) is not None
        assert db.get(FacultyMember, ids["faculty"]) is not None
        assert db.scalar(
            select(department_administrator_departments.c.department_id).where(
                department_administrator_departments.c.department_administrator_id
                == ids["administrator"],
                department_administrator_departments.c.department_id
                == ids["department"],
            )
        ) == ids["department"]


@pytest.mark.parametrize("path_key,path_prefix", [
    ("department", "/departments"),
    ("administrator", "/department_administrators"),
])
def test_deletion_preserves_existing_authentication_boundary(
    deletion_boundary, path_key, path_prefix
):
    client, _, ids, tokens = deletion_boundary
    path = f"{path_prefix}/{ids[path_key]}"

    assert client.delete(path).status_code == 401
    response = client.delete(
        path,
        headers={"Authorization": f"Bearer {tokens['department']}"},
    )
    assert response.status_code == 403


def test_non_deletion_reads_remain_available(deletion_boundary):
    client, _, ids, tokens = deletion_boundary
    super_headers = {"Authorization": f"Bearer {tokens['super']}"}
    department_headers = {"Authorization": f"Bearer {tokens['department']}"}

    assert client.get(
        f"/departments/{ids['department']}", headers=super_headers
    ).status_code == 200
    assert client.get(
        f"/department_administrators/{ids['administrator']}",
        headers=super_headers,
    ).status_code == 200
    assert client.get(
        f"/departments/{ids['department']}", headers=department_headers
    ).status_code == 200


def test_repositories_reject_direct_deletion_without_database_work(
    deletion_boundary,
):
    from app.repositories.department_administrator_repository import (
        DepartmentAdministratorRepository,
    )
    from app.repositories.department_repository import DepartmentRepository
    from app.services.administrative_deletion import AdministrativeDeletionDisabled

    _, engine, ids, _ = deletion_boundary
    with Session(engine) as db:
        for repository, record_id in (
            (DepartmentRepository(db), ids["department"]),
            (DepartmentAdministratorRepository(db), ids["administrator"]),
        ):
            with pytest.raises(AdministrativeDeletionDisabled):
                repository.delete(record_id)
        assert not db.dirty
        assert not db.deleted

