from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.deps.database import get_db
from app.api.schemas.role import RoleCreate, RoleUpdate, RoleRead
from app.repositories.role_repository import RoleRepository

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("/", response_model=List[RoleRead])
def get_all_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    repo = RoleRepository(db)
    return repo.get_all(skip=skip, limit=limit)


@router.get("/{role_id}", response_model=RoleRead)
def get_role(role_id: str, db: Session = Depends(get_db)):
    repo = RoleRepository(db)
    role = repo.get(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.post("/", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
def create_role(role_in: RoleCreate, db: Session = Depends(get_db)):
    repo = RoleRepository(db)
    return repo.create(role_in.model_dump())


@router.put("/{role_id}", response_model=RoleRead)
def update_role(role_id: str, role_in: RoleUpdate, db: Session = Depends(get_db)):
    repo = RoleRepository(db)
    role = repo.get(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return repo.update(role, role_in.model_dump(exclude_unset=True))


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(role_id: str, db: Session = Depends(get_db)):
    repo = RoleRepository(db)
    if not repo.delete(role_id):
        raise HTTPException(status_code=404, detail="Role not found")
