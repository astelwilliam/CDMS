from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.deps.database import get_db
from app.api.schemas.announcement import AnnouncementCreate, AnnouncementUpdate, AnnouncementRead
from app.repositories.announcement_repository import AnnouncementRepository

router = APIRouter(prefix="/announcements", tags=["Announcements"])


@router.get("/", response_model=List[AnnouncementRead])
def get_all_announcements(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    repo = AnnouncementRepository(db)
    return repo.get_all(skip=skip, limit=limit)


@router.get("/{announcement_id}", response_model=AnnouncementRead)
def get_announcement(announcement_id: str, db: Session = Depends(get_db)):
    repo = AnnouncementRepository(db)
    announcement = repo.get(announcement_id)
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return announcement


@router.post("/", response_model=AnnouncementRead, status_code=status.HTTP_201_CREATED)
def create_announcement(announcement_in: AnnouncementCreate, db: Session = Depends(get_db)):
    repo = AnnouncementRepository(db)
    return repo.create(announcement_in.model_dump())


@router.put("/{announcement_id}", response_model=AnnouncementRead)
def update_announcement(announcement_id: str, announcement_in: AnnouncementUpdate, db: Session = Depends(get_db)):
    repo = AnnouncementRepository(db)
    announcement = repo.get(announcement_id)
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return repo.update(announcement, announcement_in.model_dump(exclude_unset=True))


@router.delete("/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_announcement(announcement_id: str, db: Session = Depends(get_db)):
    repo = AnnouncementRepository(db)
    if not repo.delete(announcement_id):
        raise HTTPException(status_code=404, detail="Announcement not found")
