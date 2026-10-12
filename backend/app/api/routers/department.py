from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.deps.database import get_db
from app.api.deps.auth import (
    DepartmentAdministratorContext,
    get_current_super_admin,
    get_department_read_context,
)
from app.api.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentRead
from app.repositories.department_repository import DepartmentRepository

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.get("/", response_model=List[DepartmentRead])
def get_all_departments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    access: DepartmentAdministratorContext | None = Depends(get_department_read_context),
):
    repo = DepartmentRepository(db)
    if access is not None:
        return repo.get_assigned(access.department_ids, skip=skip, limit=limit)
    return repo.get_all(skip=skip, limit=limit)


@router.get("/{department_id}", response_model=DepartmentRead)
def get_department(
    department_id: str,
    db: Session = Depends(get_db),
    access: DepartmentAdministratorContext | None = Depends(get_department_read_context),
):
    repo = DepartmentRepository(db)
    department = (
        repo.get(department_id)
        if access is None
        else repo.get_assigned_by_id(department_id, access.department_ids)
    )
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return department


@router.post(
    "/",
    response_model=DepartmentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_super_admin)],
)
def create_department(department_in: DepartmentCreate, db: Session = Depends(get_db)):
    repo = DepartmentRepository(db)
    return repo.create(department_in.model_dump())


@router.put(
    "/{department_id}",
    response_model=DepartmentRead,
    dependencies=[Depends(get_current_super_admin)],
)
def update_department(department_id: str, department_in: DepartmentUpdate, db: Session = Depends(get_db)):
    repo = DepartmentRepository(db)
    department = repo.get(department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return repo.update(department, department_in.model_dump(exclude_unset=True))


@router.delete(
    "/{department_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_super_admin)],
)
def delete_department(department_id: str, db: Session = Depends(get_db)):
    repo = DepartmentRepository(db)
    if not repo.delete(department_id):
        raise HTTPException(status_code=404, detail="Department not found")
