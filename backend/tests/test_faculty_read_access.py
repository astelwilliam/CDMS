from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool


@pytest.fixture(scope="module")
def faculty_access():
    with pytest.MonkeyPatch.context() as patch:
        patch.setenv("DATABASE_URL", "sqlite://")
        patch.setenv("SECRET_KEY", "isolated-faculty-read-test-key")
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
            role = Role(name="faculty-read-role")
            college = College(name="Faculty Read College")
            db.add_all([role, college])
            db.flush()

            departments = {
                "first": Department(id="faculty-department-a", name="First", college_id=college.id),
                "second": Department(id="faculty-department-b", name="Second", college_id=college.id),
                "outside": Department(id="faculty-department-c", name="Outside", college_id=college.id),
                "deleted": Department(
                    id="faculty-department-d",
                    name="Deleted Parent",
                    college_id=college.id,
                    deleted_at=datetime.now(timezone.utc),
                ),
            }
            users = {
                "super": User(
                    email="faculty-super@example.com",
                    hashed_password="unused",
                    role="super_admin",
                    is_active=True,
                ),
                "department": User(
                    email="faculty-department@example.com",
                    hashed_password="unused",
                    role="department_admin",
                    is_active=True,
                ),
                "unlinked": User(
                    email="faculty-unlinked@example.com",
                    hashed_password="unused",
                    role="department_admin",
                    is_active=True,
                ),
                "empty": User(
                    email="faculty-empty@example.com",
                    hashed_password="unused",
                    role="department_admin",
                    is_active=True,
                ),
                "unknown": User(
                    email="faculty-unknown@example.com",
                    hashed_password="unused",
                    role="unknown_role",
                    is_active=True,
                ),
            }
            db.add_all([*departments.values(), *users.values()])
            db.flush()

            administrator = DepartmentAdministrator(
                name="Faculty Reader",
                email="faculty-reader@example.com",
                role_id=role.id,
                user_id=users["department"].id,
            )
            empty_administrator = DepartmentAdministrator(
                name="Empty Faculty Reader",
                email="empty-faculty-reader@example.com",
                role_id=role.id,
                user_id=users["empty"].id,
            )
            db.add_all([administrator, empty_administrator])
            db.flush()
            db.execute(
                department_administrator_departments.insert(),
                [
                    {
                        "department_administrator_id": administrator.id,
                        "department_id": departments[name].id,
                    }
                    for name in ("first", "second", "deleted")
                ],
            )

            faculty = {
                "first": FacultyMember(id="faculty-a", name="First Faculty", department_id=departments["first"].id),
                "second": FacultyMember(id="faculty-b", name="Second Faculty", department_id=departments["second"].id),
                "outside": FacultyMember(id="faculty-c", name="Outside Faculty", department_id=departments["outside"].id),
                "deleted": FacultyMember(
                    id="faculty-d",
                    name="Deleted Faculty",
                    department_id=departments["first"].id,
                    deleted_at=datetime.now(timezone.utc),
                ),
                "deleted_parent": FacultyMember(
                    id="faculty-e",
                    name="Deleted Parent Faculty",
                    department_id=departments["deleted"].id,
                ),
            }
            db.add_all(faculty.values())
            db.commit()

            ids = {
                "administrator": administrator.id,
                "second_department": departments["second"].id,
                "faculty": {name: item.id for name, item in faculty.items()},
            }
            tokens = {
                name: create_access_token(
                    {
                        "sub": user.id,
                        "role": "super_admin" if name != "super" else "department_admin",
                    }
                )
                for name, user in users.items()
            }

        def isolated_db():
            with Session(engine) as db:
                yield db

        previous_overrides = app.dependency_overrides.copy()
        app.dependency_overrides[get_db] = isolated_db
        try:
            with TestClient(app) as client:
                yield (
                    client,
                    tokens,
                    ids,
                    engine,
                    department_administrator_departments,
                )
        finally:
            app.dependency_overrides.clear()
            app.dependency_overrides.update(previous_overrides)
            engine.dispose()


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_super_admin_faculty_reads_remain_unrestricted(faculty_access):
    client, tokens, ids, _, _ = faculty_access
    response = client.get("/faculty_members/", headers=auth(tokens["super"]))
    assert response.status_code == 200
    assert {item["id"] for item in response.json()} == set(ids["faculty"].values())
    assert client.get(
        f"/faculty_members/{ids['faculty']['outside']}",
        headers=auth(tokens["super"]),
    ).status_code == 200


def test_department_admin_list_is_scoped_before_pagination(faculty_access):
    client, tokens, _, _, _ = faculty_access
    response = client.get(
        "/faculty_members/?skip=1&limit=1&department_id=faculty-department-c",
        headers=auth(tokens["department"]),
    )
    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == ["faculty-b"]


def test_department_admin_detail_hides_unavailable_faculty(faculty_access):
    client, tokens, ids, _, _ = faculty_access
    assert client.get(
        f"/faculty_members/{ids['faculty']['first']}",
        headers=auth(tokens["department"]),
    ).status_code == 200

    for faculty_id in (
        ids["faculty"]["outside"],
        ids["faculty"]["deleted"],
        ids["faculty"]["deleted_parent"],
        "missing-faculty",
    ):
        response = client.get(
            f"/faculty_members/{faculty_id}", headers=auth(tokens["department"])
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "Faculty member not found"}


@pytest.mark.parametrize("credential", ["unlinked", "empty", "unknown"])
def test_invalid_department_identity_is_denied(faculty_access, credential):
    client, tokens, _, _, _ = faculty_access
    response = client.get("/faculty_members/", headers=auth(tokens[credential]))
    assert response.status_code == 403
    assert response.json() == {
        "detail": "Department administrator access unavailable"
    }


def test_assignment_revocation_applies_on_next_request(faculty_access):
    client, tokens, ids, engine, assignment_table = faculty_access
    assignment = {
        "department_administrator_id": ids["administrator"],
        "department_id": ids["second_department"],
    }
    try:
        with Session(engine) as db:
            db.execute(
                delete(assignment_table).where(
                    assignment_table.c.department_administrator_id
                    == ids["administrator"],
                    assignment_table.c.department_id == ids["second_department"],
                )
            )
            db.commit()

        response = client.get(
            f"/faculty_members/{ids['faculty']['second']}",
            headers=auth(tokens["department"]),
        )
        assert response.status_code == 404
    finally:
        with Session(engine) as db:
            db.execute(assignment_table.insert(), assignment)
            db.commit()


@pytest.mark.parametrize(
    "method,path",
    [
        ("PUT", "/faculty_members/faculty-a"),
        ("DELETE", "/faculty_members/faculty-a"),
    ],
)
def test_faculty_writes_remain_super_admin_only(
    faculty_access, method, path
):
    client, tokens, _, _, _ = faculty_access
    response = client.request(method, path, headers=auth(tokens["department"]), json={})
    assert response.status_code == 403
