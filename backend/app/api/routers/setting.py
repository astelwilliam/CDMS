from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.deps.database import get_db
from app.api.schemas.setting import SettingCreate, SettingUpdate, SettingRead
from app.repositories.setting_repository import SettingRepository

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("/", response_model=List[SettingRead])
def get_all_settings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    repo = SettingRepository(db)
    return repo.get_all(skip=skip, limit=limit)


@router.get("/{setting_id}", response_model=SettingRead)
def get_setting(setting_id: str, db: Session = Depends(get_db)):
    repo = SettingRepository(db)
    setting = repo.get(setting_id)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting


@router.post("/", response_model=SettingRead, status_code=status.HTTP_201_CREATED)
def create_setting(setting_in: SettingCreate, db: Session = Depends(get_db)):
    repo = SettingRepository(db)
    return repo.create(setting_in.model_dump())


@router.put("/{setting_id}", response_model=SettingRead)
def update_setting(setting_id: str, setting_in: SettingUpdate, db: Session = Depends(get_db)):
    repo = SettingRepository(db)
    setting = repo.get(setting_id)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return repo.update(setting, setting_in.model_dump(exclude_unset=True))


@router.delete("/{setting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_setting(setting_id: str, db: Session = Depends(get_db)):
    repo = SettingRepository(db)
    if not repo.delete(setting_id):
        raise HTTPException(status_code=404, detail="Setting not found")
