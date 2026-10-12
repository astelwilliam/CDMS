from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.deps.database import get_db
from app.api.schemas.department_administrator import DepartmentAdministratorCreate, DepartmentAdministratorUpdate, DepartmentAdministratorRead
from app.repositories.department_administrator_repository import DepartmentAdministratorRepository
from app.services.administrative_deletion import (
    AdministrativeDeletionDisabled,
    DELETION_DISABLED_DETAIL,
)

router = APIRouter(prefix="/department_administrators", tags=["Department Administrators"])


@router.get("/", response_model=List[DepartmentAdministratorRead])
def get_all_admins(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    repo = DepartmentAdministratorRepository(db)
    return repo.get_all(skip=skip, limit=limit)


@router.get("/{admin_id}", response_model=DepartmentAdministratorRead)
def get_admin(admin_id: str, db: Session = Depends(get_db)):
    repo = DepartmentAdministratorRepository(db)
    admin = repo.get(admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Department administrator not found")
    return admin


@router.post("/", response_model=DepartmentAdministratorRead, status_code=status.HTTP_201_CREATED)
def create_admin(admin_in: DepartmentAdministratorCreate, db: Session = Depends(get_db)):
    repo = DepartmentAdministratorRepository(db)
    return repo.create(admin_in.model_dump())


@router.put("/{admin_id}", response_model=DepartmentAdministratorRead)
def update_admin(admin_id: str, admin_in: DepartmentAdministratorUpdate, db: Session = Depends(get_db)):
    repo = DepartmentAdministratorRepository(db)
    admin = repo.get(admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Department administrator not found")
    return repo.update(admin, admin_in.model_dump(exclude_unset=True))


@router.delete("/{admin_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin(admin_id: str, db: Session = Depends(get_db)):
    repo = DepartmentAdministratorRepository(db)
    try:
        repo.delete(admin_id)
    except AdministrativeDeletionDisabled as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=DELETION_DISABLED_DETAIL,
        ) from exc
