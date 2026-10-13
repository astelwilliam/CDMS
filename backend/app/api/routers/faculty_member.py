from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.deps.auth import (
    DepartmentAdministratorContext,
    get_current_super_admin,
    get_department_read_context,
)
from app.api.deps.database import get_db
from app.api.schemas.faculty_member import FacultyMemberCreate, FacultyMemberUpdate, FacultyMemberRead
from app.api.schemas.auth import CurrentUser
from app.repositories.faculty_member_repository import FacultyMemberRepository
from app.services.privileged_faculty_mutation import (
    FacultyMutationTargetNotFound,
    FacultyMutationTemporarilyUnavailable,
    PrivilegedFacultyMutationDenied,
    create_faculty_as_super_admin,
    soft_delete_faculty_as_super_admin,
    update_faculty_as_super_admin,
)

router = APIRouter(prefix="/faculty_members", tags=["Faculty Members"])


def _raise_temporary_failure(exc: FacultyMutationTemporarilyUnavailable) -> None:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Faculty mutation temporarily unavailable",
        headers={"Retry-After": "1"},
    ) from exc


@router.get("/", response_model=List[FacultyMemberRead])
def get_all_faculty_members(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    access: DepartmentAdministratorContext | None = Depends(get_department_read_context),
):
    repo = FacultyMemberRepository(db)
    if access is not None:
        return repo.get_assigned(access.department_ids, skip=skip, limit=limit)
    return repo.get_all(skip=skip, limit=limit)


@router.get("/{faculty_member_id}", response_model=FacultyMemberRead)
def get_faculty_member(
    faculty_member_id: str,
    db: Session = Depends(get_db),
    access: DepartmentAdministratorContext | None = Depends(get_department_read_context),
):
    repo = FacultyMemberRepository(db)
    faculty = (
        repo.get(faculty_member_id)
        if access is None
        else repo.get_assigned_by_id(faculty_member_id, access.department_ids)
    )
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty member not found")
    return faculty


@router.post(
    "/",
    response_model=FacultyMemberRead,
    status_code=status.HTTP_201_CREATED,
)
def create_faculty_member(
    faculty_in: FacultyMemberCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_super_admin),
):
    values = faculty_in.model_dump()
    department_id = values.pop("department_id")
    try:
        return create_faculty_as_super_admin(
            db, current_user.id, department_id, values
        )
    except FacultyMutationTargetNotFound as exc:
        raise HTTPException(status_code=404, detail="Department not found") from exc
    except PrivilegedFacultyMutationDenied as exc:
        raise HTTPException(status_code=403, detail="Access denied") from exc
    except FacultyMutationTemporarilyUnavailable as exc:
        _raise_temporary_failure(exc)


@router.put(
    "/{faculty_member_id}",
    response_model=FacultyMemberRead,
)
def update_faculty_member(
    faculty_member_id: str,
    faculty_in: FacultyMemberUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_super_admin),
):
    try:
        return update_faculty_as_super_admin(
            db,
            current_user.id,
            faculty_member_id,
            faculty_in.model_dump(exclude_unset=True),
        )
    except FacultyMutationTargetNotFound as exc:
        raise HTTPException(status_code=404, detail="Faculty member not found") from exc
    except PrivilegedFacultyMutationDenied as exc:
        raise HTTPException(status_code=403, detail="Access denied") from exc
    except FacultyMutationTemporarilyUnavailable as exc:
        _raise_temporary_failure(exc)


@router.delete(
    "/{faculty_member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_faculty_member(
    faculty_member_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_super_admin),
):
    try:
        soft_delete_faculty_as_super_admin(db, current_user.id, faculty_member_id)
    except FacultyMutationTargetNotFound as exc:
        raise HTTPException(status_code=404, detail="Faculty member not found") from exc
    except PrivilegedFacultyMutationDenied as exc:
        raise HTTPException(status_code=403, detail="Access denied") from exc
    except FacultyMutationTemporarilyUnavailable as exc:
        _raise_temporary_failure(exc)
