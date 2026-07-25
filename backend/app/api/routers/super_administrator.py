from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.deps.database import get_db
from app.api.schemas.super_administrator import SuperAdministratorCreate, SuperAdministratorUpdate, SuperAdministratorRead
from app.repositories.super_administrator_repository import SuperAdministratorRepository

router = APIRouter(prefix="/super_administrators", tags=["Super Administrators"])


@router.get("/", response_model=List[SuperAdministratorRead])
def get_all_super_admins(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    repo = SuperAdministratorRepository(db)
    return repo.get_all(skip=skip, limit=limit)


@router.get("/{admin_id}", response_model=SuperAdministratorRead)
def get_super_admin(admin_id: str, db: Session = Depends(get_db)):
    repo = SuperAdministratorRepository(db)
    admin = repo.get(admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Super administrator not found")
    return admin


@router.post("/", response_model=SuperAdministratorRead, status_code=status.HTTP_201_CREATED)
def create_super_admin(admin_in: SuperAdministratorCreate, db: Session = Depends(get_db)):
    repo = SuperAdministratorRepository(db)
    return repo.create(admin_in.model_dump())


@router.put("/{admin_id}", response_model=SuperAdministratorRead)
def update_super_admin(admin_id: str, admin_in: SuperAdministratorUpdate, db: Session = Depends(get_db)):
    repo = SuperAdministratorRepository(db)
    admin = repo.get(admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Super administrator not found")
    return repo.update(admin, admin_in.model_dump(exclude_unset=True))


@router.delete("/{admin_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_super_admin(admin_id: str, db: Session = Depends(get_db)):
    repo = SuperAdministratorRepository(db)
    if not repo.delete(admin_id):
        raise HTTPException(status_code=404, detail="Super administrator not found")
