from collections.abc import Mapping

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.department import Department
from app.models.faculty_member import FacultyMember
from app.models.user import User
from app.repositories.faculty_member_repository import FacultyMemberRepository


class PrivilegedFacultyMutationDenied(Exception):
    """The current database user is not an active super administrator."""


class FacultyMutationTargetNotFound(Exception):
    """The faculty member or its active owning department is unavailable."""


def _lock_super_admin(db: Session, user_id: str) -> User:
    user = db.scalar(select(User).where(User.id == user_id).with_for_update())
    if user is None or not user.is_active or user.role != "super_admin":
        raise PrivilegedFacultyMutationDenied
    return user


def _lock_active_department(db: Session, department_id: str) -> Department:
    department = db.scalar(
        select(Department)
        .where(Department.id == department_id)
        .with_for_update()
    )
    if department is None or department.deleted_at is not None:
        raise FacultyMutationTargetNotFound
    return department


def _lock_faculty_target(
    db: Session,
    repository: FacultyMemberRepository,
    faculty_member_id: str,
) -> FacultyMember:
    department_id = db.scalar(
        select(FacultyMember.department_id).where(
            FacultyMember.id == faculty_member_id,
            FacultyMember.deleted_at.is_(None),
        )
    )
    if department_id is None:
        raise FacultyMutationTargetNotFound
    _lock_active_department(db, department_id)
    faculty = repository.get_for_scoped_write(faculty_member_id, department_id)
    if faculty is None:
        raise FacultyMutationTargetNotFound
    return faculty


def create_faculty_as_super_admin(
    db: Session,
    user_id: str,
    department_id: str,
    values: Mapping[str, object],
) -> FacultyMember:
    repository = FacultyMemberRepository(db)
    try:
        _lock_super_admin(db, user_id)
        _lock_active_department(db, department_id)
        faculty = repository.add_for_scoped_write(department_id, values)
        db.commit()
        db.refresh(faculty)
        return faculty
    except Exception:
        db.rollback()
        raise


def update_faculty_as_super_admin(
    db: Session,
    user_id: str,
    faculty_member_id: str,
    values: Mapping[str, object],
) -> FacultyMember:
    repository = FacultyMemberRepository(db)
    try:
        _lock_super_admin(db, user_id)
        faculty = _lock_faculty_target(db, repository, faculty_member_id)
        repository.update_for_scoped_write(faculty, values)
        db.commit()
        db.refresh(faculty)
        return faculty
    except Exception:
        db.rollback()
        raise


def soft_delete_faculty_as_super_admin(
    db: Session,
    user_id: str,
    faculty_member_id: str,
) -> None:
    repository = FacultyMemberRepository(db)
    try:
        _lock_super_admin(db, user_id)
        faculty = _lock_faculty_target(db, repository, faculty_member_id)
        repository.soft_delete_for_scoped_write(faculty)
        db.commit()
    except Exception:
        db.rollback()
        raise
