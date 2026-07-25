from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.deps.database import get_db
from app.api.schemas.permission import PermissionCreate, PermissionUpdate, PermissionRead
from app.repositories.permission_repository import PermissionRepository

router = APIRouter(prefix="/permissions", tags=["Permissions"])


@router.get("/", response_model=List[PermissionRead])
def get_all_permissions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    repo = PermissionRepository(db)
    return repo.get_all(skip=skip, limit=limit)


@router.get("/{permission_id}", response_model=PermissionRead)
def get_permission(permission_id: str, db: Session = Depends(get_db)):
    repo = PermissionRepository(db)
    permission = repo.get(permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return permission


@router.post("/", response_model=PermissionRead, status_code=status.HTTP_201_CREATED)
def create_permission(permission_in: PermissionCreate, db: Session = Depends(get_db)):
    repo = PermissionRepository(db)
    return repo.create(permission_in.model_dump())


@router.put("/{permission_id}", response_model=PermissionRead)
def update_permission(permission_id: str, permission_in: PermissionUpdate, db: Session = Depends(get_db)):
    repo = PermissionRepository(db)
    permission = repo.get(permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return repo.update(permission, permission_in.model_dump(exclude_unset=True))


@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_permission(permission_id: str, db: Session = Depends(get_db)):
    repo = PermissionRepository(db)
    if not repo.delete(permission_id):
        raise HTTPException(status_code=404, detail="Permission not found")
