from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.gallery_album import GalleryAlbum
from app.repositories.base import BaseRepository


class GalleryAlbumRepository(BaseRepository[GalleryAlbum]):
    """Repository for GalleryAlbum entity."""

    def __init__(self, db: Session):
        super().__init__(GalleryAlbum, db)

    def get_by_department(self, department_id: str, skip: int = 0, limit: int = 100) -> List[GalleryAlbum]:
        stmt = (
            select(GalleryAlbum)
            .where(GalleryAlbum.department_id == department_id, GalleryAlbum.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
