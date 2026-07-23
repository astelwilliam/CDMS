from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.gallery_image import GalleryImage
from app.repositories.base import BaseRepository


class GalleryImageRepository(BaseRepository[GalleryImage]):
    """Repository for GalleryImage entity."""

    def __init__(self, db: Session):
        super().__init__(GalleryImage, db)

    def get_by_album(self, album_id: str, skip: int = 0, limit: int = 100) -> List[GalleryImage]:
        stmt = (
            select(GalleryImage)
            .where(GalleryImage.gallery_album_id == album_id, GalleryImage.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
