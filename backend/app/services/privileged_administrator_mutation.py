from dataclasses import dataclass

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.association_tables import department_administrator_departments
from app.models.department import Department
from app.models.department_administrator import DepartmentAdministrator
from app.models.user import User


class PrivilegedAdministratorMutationDenied(Exception):
    """The actor or target identity is not eligible for this mutation."""


class AdministratorMutationTargetNotFound(Exception):
    """The administrator target does not exist."""


class DepartmentMutationTargetNotFound(Exception):
    """The department target does not exist or is deleted."""


@dataclass(frozen=True)
class LockedAssignmentMutation:
    actor: User
    linked_user: User
    administrator: DepartmentAdministrator
    department: Department
    assignment_department_ids: frozenset[str]


def _lock_users(db: Session, user_ids: set[str]) -> dict[str, User]:
    return {
        user.id: user
        for user in db.scalars(
            select(User)
            .where(User.id.in_(user_ids))
            .order_by(User.id)
            .with_for_update()
        )
    }


def _require_super_admin(users: dict[str, User], actor_user_id: str) -> User:
    actor = users.get(actor_user_id)
    if actor is None or not actor.is_active or actor.role != "super_admin":
        raise PrivilegedAdministratorMutationDenied
    return actor


def _lock_assignment_mutation(
    db: Session,
    actor_user_id: str,
    administrator_id: str,
    department_id: str,
) -> LockedAssignmentMutation:
    linked_user_id = db.scalar(
        select(DepartmentAdministrator.user_id).where(
            DepartmentAdministrator.id == administrator_id
        )
    )
    if linked_user_id is None:
        raise PrivilegedAdministratorMutationDenied

    users = _lock_users(db, {actor_user_id, linked_user_id})
    actor = _require_super_admin(users, actor_user_id)
    linked_user = users.get(linked_user_id)
    if (
        linked_user is None
        or not linked_user.is_active
        or linked_user.role != "department_admin"
    ):
        raise PrivilegedAdministratorMutationDenied

    administrator = db.scalar(
        select(DepartmentAdministrator)
        .where(
            DepartmentAdministrator.id == administrator_id,
            DepartmentAdministrator.user_id == linked_user.id,
        )
        .with_for_update()
    )
    if administrator is None:
        raise AdministratorMutationTargetNotFound

    assigned_department_ids = list(
        db.scalars(
            select(department_administrator_departments.c.department_id)
            .where(
                department_administrator_departments.c.department_administrator_id
                == administrator.id
            )
            .order_by(department_administrator_departments.c.department_id)
        )
    )
    department_ids_to_lock = sorted(
        set(assigned_department_ids) | {department_id}
    )
    departments = list(
        db.scalars(
            select(Department)
            .where(Department.id.in_(department_ids_to_lock))
            .order_by(Department.id)
            .with_for_update()
        )
    )
    departments_by_id = {department.id: department for department in departments}

    locked_assignment_ids = frozenset(
        db.scalars(
            select(department_administrator_departments.c.department_id)
            .where(
                department_administrator_departments.c.department_administrator_id
                == administrator.id
            )
            .order_by(department_administrator_departments.c.department_id)
            .with_for_update()
        )
    )
    department = departments_by_id.get(department_id)
    if department is None or department.deleted_at is not None:
        raise DepartmentMutationTargetNotFound

    return LockedAssignmentMutation(
        actor=actor,
        linked_user=linked_user,
        administrator=administrator,
        department=department,
        assignment_department_ids=locked_assignment_ids,
    )


def stage_department_assignment(
    db: Session,
    actor_user_id: str,
    administrator_id: str,
    department_id: str,
) -> bool:
    """Stage a same-college assignment without committing or rolling back."""
    locked = _lock_assignment_mutation(
        db, actor_user_id, administrator_id, department_id
    )
    if department_id in locked.assignment_department_ids:
        return False

    existing_college_ids = set(
        db.scalars(
            select(Department.college_id).where(
                Department.id.in_(locked.assignment_department_ids),
                Department.deleted_at.is_(None),
            )
        )
    )
    if existing_college_ids and existing_college_ids != {locked.department.college_id}:
        raise PrivilegedAdministratorMutationDenied

    db.execute(
        department_administrator_departments.insert().values(
            department_administrator_id=locked.administrator.id,
            department_id=locked.department.id,
        )
    )
    return True


def stage_department_assignment_revocation(
    db: Session,
    actor_user_id: str,
    administrator_id: str,
    department_id: str,
) -> bool:
    """Stage assignment revocation without committing or rolling back."""
    locked = _lock_assignment_mutation(
        db, actor_user_id, administrator_id, department_id
    )
    if department_id not in locked.assignment_department_ids:
        return False

    db.execute(
        delete(department_administrator_departments).where(
            department_administrator_departments.c.department_administrator_id
            == locked.administrator.id,
            department_administrator_departments.c.department_id
            == locked.department.id,
        )
    )
    return True


def stage_administrator_identity_change(
    db: Session,
    actor_user_id: str,
    administrator_id: str,
    new_user_id: str | None,
) -> DepartmentAdministrator:
    """Stage identity linking, unlinking, or relinking without committing."""
    current_user_id = db.scalar(
        select(DepartmentAdministrator.user_id).where(
            DepartmentAdministrator.id == administrator_id
        )
    )
    user_ids = {actor_user_id}
    if current_user_id is not None:
        user_ids.add(current_user_id)
    if new_user_id is not None:
        user_ids.add(new_user_id)

    users = _lock_users(db, user_ids)
    _require_super_admin(users, actor_user_id)
    if new_user_id is not None:
        new_user = users.get(new_user_id)
        if (
            new_user is None
            or not new_user.is_active
            or new_user.role != "department_admin"
        ):
            raise PrivilegedAdministratorMutationDenied

    administrator_filter = DepartmentAdministrator.id == administrator_id
    if new_user_id is not None:
        administrator_filter = administrator_filter | (
            DepartmentAdministrator.user_id == new_user_id
        )

    administrators = list(
        db.scalars(
            select(DepartmentAdministrator)
            .where(administrator_filter)
            .order_by(DepartmentAdministrator.id)
            .with_for_update()
        )
    )
    administrator = next(
        (item for item in administrators if item.id == administrator_id), None
    )
    if administrator is None:
        raise AdministratorMutationTargetNotFound
    if administrator.user_id != current_user_id:
        raise PrivilegedAdministratorMutationDenied
    if any(
        item.id != administrator.id and item.user_id == new_user_id
        for item in administrators
    ):
        raise PrivilegedAdministratorMutationDenied

    administrator.user_id = new_user_id
    db.flush()
    return administrator
