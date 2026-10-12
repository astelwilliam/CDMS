from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool


@pytest.fixture(scope="module")
def department_access():
    with pytest.MonkeyPatch.context() as patch:
        patch.setenv("DATABASE_URL", "sqlite://")
        patch.setenv("SECRET_KEY", "isolated-department-read-test-key")
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
        from app.models.role import Role
        from app.models.user import User

        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(engine)

        with Session(engine) as db:
            role = Role(name="department-read-role")
            college = College(name="Department Read College")
            other_college = College(name="Other Department Read College")
            db.add_all([role, college, other_college])
            db.flush()

            departments = {
                "first": Department(id="department-a", name="First", college_id=college.id),
                "second": Department(id="department-b", name="Second", college_id=college.id),
                "outside": Department(id="department-c", name="Outside", college_id=college.id),
                "deleted": Department(
                    id="department-d",
                    name="Deleted",
                    college_id=college.id,
                    deleted_at=datetime.now(timezone.utc),
                ),
                "other_college": Department(
                    id="department-e", name="Other College", college_id=other_college.id
                ),
            }
            users = {
                "super": User(
                    email="super-read@example.com",
                    hashed_password="unused",
                    role="super_admin",
                    is_active=True,
                ),
                "department": User(
                    email="department-read@example.com",
                    hashed_password="unused",
                    role="department_admin",
                    is_active=True,
                ),
                "cross_college": User(
                    email="cross-college-read@example.com",
                    hashed_password="unused",
                    role="department_admin",
                    is_active=True,
                ),
            }
            db.add_all([*departments.values(), *users.values()])
            db.flush()

            administrator = DepartmentAdministrator(
                name="Department Reader",
                email="administrator-read@example.com",
                role_id=role.id,
                user_id=users["department"].id,
            )
            cross_college_administrator = DepartmentAdministrator(
                name="Cross College Reader",
                email="cross-college-administrator@example.com",
                role_id=role.id,
                user_id=users["cross_college"].id,
            )
            db.add_all([administrator, cross_college_administrator])
            db.flush()
            db.execute(
                department_administrator_departments.insert(),
                [
                    {
                        "department_administrator_id": administrator.id,
                        "department_id": departments[name].id,
                    }
                    for name in ("first", "second", "deleted")
                ]
                + [
                    {
                        "department_administrator_id": cross_college_administrator.id,
                        "department_id": departments[name].id,
                    }
                    for name in ("first", "other_college")
                ],
            )
            db.commit()

            ids = {
                "administrator": administrator.id,
                "departments": {name: item.id for name, item in departments.items()},
            }
            tokens = {
                "super": create_access_token(
                    {"sub": users["super"].id, "role": "department_admin"}
                ),
                "department": create_access_token(
                    {"sub": users["department"].id, "role": "super_admin"}
                ),
                "cross_college": create_access_token(
                    {"sub": users["cross_college"].id, "role": "department_admin"}
                ),
            }

        def isolated_db():
            with Session(engine) as db:
                yield db

        previous_overrides = app.dependency_overrides.copy()
        app.dependency_overrides[get_db] = isolated_db
        try:
            with TestClient(app) as client:
                yield client, tokens, ids, engine, department_administrator_departments
        finally:
            app.dependency_overrides.clear()
            app.dependency_overrides.update(previous_overrides)
            engine.dispose()


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_super_admin_department_reads_remain_unrestricted(department_access):
    client, tokens, ids, _, _ = department_access

    response = client.get("/departments/", headers=auth(tokens["super"]))
    assert response.status_code == 200
    assert {item["id"] for item in response.json()} == set(ids["departments"].values())
    assert client.get(
        f"/departments/{ids['departments']['outside']}", headers=auth(tokens["super"])
    ).status_code == 200


def test_department_admin_list_is_scoped_before_pagination(department_access):
    client, tokens, _, _, _ = department_access

    response = client.get(
        "/departments/?skip=1&limit=1&college_id=untrusted",
        headers=auth(tokens["department"]),
    )

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == ["department-b"]


def test_department_admin_detail_hides_unavailable_departments(department_access):
    client, tokens, ids, _, _ = department_access

    assert client.get(
        f"/departments/{ids['departments']['first']}",
        headers=auth(tokens["department"]),
    ).status_code == 200
    for department_id in (
        ids["departments"]["outside"],
        ids["departments"]["deleted"],
        "missing-department",
    ):
        response = client.get(
            f"/departments/{department_id}", headers=auth(tokens["department"])
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "Department not found"}


def test_cross_college_assignments_fail_closed(department_access):
    client, tokens, _, _, _ = department_access
    response = client.get("/departments/", headers=auth(tokens["cross_college"]))
    assert response.status_code == 403


def test_assignment_removal_applies_on_next_request(department_access):
    client, tokens, ids, engine, assignment_table = department_access
    with Session(engine) as db:
        db.execute(
            delete(assignment_table).where(
                assignment_table.c.department_administrator_id == ids["administrator"],
                assignment_table.c.department_id == ids["departments"]["second"],
            )
        )
        db.commit()

    response = client.get("/departments/", headers=auth(tokens["department"]))
    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == ["department-a"]


@pytest.mark.parametrize(
    "method,path",
    [
        ("POST", "/departments/"),
        ("PUT", "/departments/department-a"),
        ("DELETE", "/departments/department-a"),
    ],
)
def test_department_writes_remain_super_admin_only(
    department_access, method, path
):
    client, tokens, _, _, _ = department_access
    response = client.request(method, path, headers=auth(tokens["department"]), json={})
    assert response.status_code == 403


def test_other_business_routers_remain_super_admin_only(department_access):
    client, tokens, _, _, _ = department_access
    response = client.get("/colleges/", headers=auth(tokens["department"]))
    assert response.status_code == 403
