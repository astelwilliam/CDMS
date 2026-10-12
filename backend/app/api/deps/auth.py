from dataclasses import dataclass
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Optional

from app.api.deps.database import get_db
from app.core.security import decode_access_token
from app.models.association_tables import department_administrator_departments
from app.models.department import Department
from app.models.department_administrator import DepartmentAdministrator
from app.services.auth_service import AuthService
from app.api.schemas.auth import CurrentUser

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> CurrentUser:
    """
    Dependency to get the current authenticated user from the JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    auth_service = AuthService(db)
    user = auth_service.get_current_user(user_id)
    
    return user


def require_role(required_role: str):
    """
    Dependency factory to enforce role-based access control.
    """
    def role_checker(current_user: CurrentUser = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}"
            )
        return current_user
    return role_checker


# Predefined role dependencies for convenience
get_current_super_admin = require_role("super_admin")
get_current_department_admin = require_role("department_admin")


@dataclass(frozen=True)
class DepartmentAdministratorContext:
    """Database-backed identity and active department assignments for an admin."""

    user: CurrentUser
    administrator_id: str
    department_ids: frozenset[str]
    college_id: str


def get_department_administrator_context(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DepartmentAdministratorContext:
    """Resolve a department administrator and their current eligible assignments."""
    access_denied = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Department administrator access unavailable",
    )

    if current_user.role != "department_admin":
        raise access_denied

    administrator_ids = list(
        db.scalars(
            select(DepartmentAdministrator.id)
            .where(DepartmentAdministrator.user_id == current_user.id)
            .limit(2)
        )
    )
    if len(administrator_ids) != 1:
        raise access_denied

    administrator_id = administrator_ids[0]
    assignments = db.execute(
        select(Department.id, Department.college_id)
        .join(
            department_administrator_departments,
            department_administrator_departments.c.department_id == Department.id,
        )
        .where(
            department_administrator_departments.c.department_administrator_id
            == administrator_id,
            Department.deleted_at.is_(None),
        )
        .order_by(Department.id)
    ).all()
    if not assignments:
        raise access_denied

    college_ids = {college_id for _, college_id in assignments}
    if len(college_ids) != 1:
        raise access_denied

    return DepartmentAdministratorContext(
        user=current_user,
        administrator_id=administrator_id,
        department_ids=frozenset(department_id for department_id, _ in assignments),
        college_id=next(iter(college_ids)),
    )
