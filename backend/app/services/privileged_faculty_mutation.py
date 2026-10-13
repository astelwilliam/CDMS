from collections.abc import Mapping

from sqlalchemy import select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.models.department import Department
from app.models.faculty_member import FacultyMember
from app.models.user import User
from app.repositories.faculty_member_repository import FacultyMemberRepository
from app.services.scoped_write_authorization import (
    ScopedWriteAccessDenied,
    ScopedWriteResourceNotFound,
    lock_department_write_access,
)


class PrivilegedFacultyMutationDenied(Exception):
    """The current database user is not an active super administrator."""


class DepartmentFacultyMutationDenied(Exception):
    """The current database user has no valid department-admin identity."""


class FacultyMutationTargetNotFound(Exception):
    """The faculty member or its active owning department is unavailable."""


class FacultyMutationTemporarilyUnavailable(Exception):
    """A transient database conflict aborted the complete mutation."""


TRANSIENT_TRANSACTION_SQLSTATES = frozenset({"40P01", "40001", "55P03"})


def _is_transient_transaction_failure(error: DBAPIError) -> bool:
    sqlstate = getattr(error.orig, "sqlstate", None) or getattr(
        error.orig, "pgcode", None
    )
    return sqlstate in TRANSIENT_TRANSACTION_SQLSTATES


def _rollback_and_raise(db: Session, error: Exception) -> None:
    db.rollback()
    if isinstance(error, DBAPIError) and _is_transient_transaction_failure(error):
        raise FacultyMutationTemporarilyUnavailable from error
    raise error


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
    except Exception as error:
        _rollback_and_raise(db, error)


def create_faculty_as_department_admin(
    db: Session,
    user_id: str,
    department_id: str,
    values: Mapping[str, object],
) -> FacultyMember:
    repository = FacultyMemberRepository(db)
    try:
        access = lock_department_write_access(db, user_id, department_id)
        faculty = repository.add_for_scoped_write(access.department.id, values)
        db.commit()
        db.refresh(faculty)
        return faculty
    except ScopedWriteAccessDenied as error:
        db.rollback()
        raise DepartmentFacultyMutationDenied from error
    except ScopedWriteResourceNotFound as error:
        db.rollback()
        raise FacultyMutationTargetNotFound from error
    except Exception as error:
        _rollback_and_raise(db, error)


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
    except Exception as error:
        _rollback_and_raise(db, error)


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
    except Exception as error:
        _rollback_and_raise(db, error)
