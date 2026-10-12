from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.association_tables import department_administrator_departments
from app.models.department import Department
from app.models.department_administrator import DepartmentAdministrator
from app.models.user import User


class ScopedWriteAccessDenied(Exception):
    """The authenticated identity is not eligible for scoped writes."""


class ScopedWriteResourceNotFound(Exception):
    """The requested department is absent, deleted, or outside the assignment."""


@dataclass(frozen=True)
class LockedDepartmentWriteAccess:
    user: User
    administrator: DepartmentAdministrator
    department: Department


def lock_department_write_access(
    db: Session,
    user_id: str,
    department_id: str,
) -> LockedDepartmentWriteAccess:
    """Lock and revalidate department-admin write access without committing."""
    user = db.scalar(
        select(User).where(User.id == user_id).with_for_update()
    )
    if user is None or not user.is_active or user.role != "department_admin":
        raise ScopedWriteAccessDenied

    administrators = list(
        db.scalars(
            select(DepartmentAdministrator)
            .where(DepartmentAdministrator.user_id == user.id)
            .order_by(DepartmentAdministrator.id)
            .limit(2)
            .with_for_update()
        )
    )
    if len(administrators) != 1:
        raise ScopedWriteAccessDenied
    administrator = administrators[0]

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

    locked_assignment_ids = list(
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
    if (
        department is None
        or department.deleted_at is not None
        or department_id not in locked_assignment_ids
    ):
        raise ScopedWriteResourceNotFound

    live_college_ids = {
        departments_by_id[assigned_id].college_id
        for assigned_id in locked_assignment_ids
        if assigned_id in departments_by_id
        and departments_by_id[assigned_id].deleted_at is None
    }
    if len(live_college_ids) != 1:
        raise ScopedWriteAccessDenied

    return LockedDepartmentWriteAccess(
        user=user,
        administrator=administrator,
        department=department,
    )
