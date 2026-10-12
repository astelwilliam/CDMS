from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Session

from app.models.faculty_member import FacultyMember
from app.repositories.faculty_member_repository import FacultyMemberRepository


def repository():
    session = MagicMock(spec=Session)
    return FacultyMemberRepository(session), session


def test_scoped_write_lookup_locks_the_owned_active_faculty_row():
    repo, session = repository()
    expected = FacultyMember(
        id="faculty-id",
        department_id="department-id",
        name="Faculty",
    )
    session.scalar.return_value = expected

    assert repo.get_for_scoped_write("faculty-id", "department-id") is expected

    statement = session.scalar.call_args.args[0]
    sql = str(
        statement.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
    )
    assert "faculty_members.id = 'faculty-id'" in sql
    assert "faculty_members.department_id = 'department-id'" in sql
    assert "faculty_members.deleted_at IS NULL" in sql
    assert sql.endswith("FOR UPDATE")


def test_scoped_create_flushes_without_committing():
    repo, session = repository()

    faculty = repo.add_for_scoped_write(
        "department-id",
        {"name": "Faculty", "title": "Professor"},
    )

    assert faculty.department_id == "department-id"
    assert faculty.name == "Faculty"
    session.add.assert_called_once_with(faculty)
    session.flush.assert_called_once_with()
    session.commit.assert_not_called()
    session.rollback.assert_not_called()


@pytest.mark.parametrize("field", ["id", "department_id", "deleted_at"])
def test_scoped_create_rejects_system_and_ownership_fields(field):
    repo, session = repository()

    with pytest.raises(ValueError, match=field):
        repo.add_for_scoped_write(
            "verified-department",
            {"name": "Faculty", field: "untrusted"},
        )

    session.add.assert_not_called()
    session.flush.assert_not_called()
    session.commit.assert_not_called()


def test_scoped_update_changes_content_without_committing_or_moving_owner():
    repo, session = repository()
    faculty = FacultyMember(
        id="faculty-id",
        department_id="department-id",
        name="Before",
    )

    result = repo.update_for_scoped_write(
        faculty,
        {"name": "After", "biography": "Updated"},
    )

    assert result is faculty
    assert faculty.name == "After"
    assert faculty.biography == "Updated"
    assert faculty.department_id == "department-id"
    session.flush.assert_called_once_with()
    session.commit.assert_not_called()
    session.rollback.assert_not_called()


@pytest.mark.parametrize("field", ["id", "department_id", "deleted_at"])
def test_scoped_update_rejects_system_and_ownership_fields(field):
    repo, session = repository()
    faculty = FacultyMember(
        id="faculty-id",
        department_id="department-id",
        name="Before",
    )

    with pytest.raises(ValueError, match=field):
        repo.update_for_scoped_write(faculty, {field: "untrusted"})

    assert faculty.department_id == "department-id"
    assert faculty.deleted_at is None
    session.flush.assert_not_called()
    session.commit.assert_not_called()


def test_scoped_delete_uses_database_time_without_hard_delete_or_commit():
    repo, session = repository()
    database_time = datetime(2026, 1, 2, tzinfo=timezone.utc)
    session.scalar.return_value = database_time
    faculty = FacultyMember(
        id="faculty-id",
        department_id="department-id",
        name="Faculty",
    )

    assert repo.soft_delete_for_scoped_write(faculty) is faculty
    assert faculty.deleted_at == database_time
    session.delete.assert_not_called()
    session.flush.assert_called_once_with()
    session.commit.assert_not_called()
    session.rollback.assert_not_called()


def test_scoped_delete_cannot_restore_or_repeat_a_delete():
    repo, session = repository()
    faculty = FacultyMember(
        id="faculty-id",
        department_id="department-id",
        name="Faculty",
        deleted_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
    )

    with pytest.raises(ValueError, match="already deleted"):
        repo.soft_delete_for_scoped_write(faculty)

    session.scalar.assert_not_called()
    session.flush.assert_not_called()
    session.delete.assert_not_called()
    session.commit.assert_not_called()
