from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.announcement import Announcement
from app.repositories.base import BaseRepository


class AnnouncementRepository(BaseRepository[Announcement]):
    """Repository for Announcement entity."""

    def __init__(self, db: Session):
        super().__init__(Announcement, db)

    def get_by_department(self, department_id: str, skip: int = 0, limit: int = 100) -> List[Announcement]:
        stmt = (
            select(Announcement)
            .where(Announcement.department_id == department_id, Announcement.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_published(self, skip: int = 0, limit: int = 100) -> List[Announcement]:
        """Get currently published announcements."""
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        stmt = (
            select(Announcement)
            .where(
                Announcement.lifecycle_status == "Published",
                Announcement.deleted_at.is_(None),
                (Announcement.publication_date <= now) | (Announcement.publication_date.is_(None)),
                (Announcement.expiration_date > now) | (Announcement.expiration_date.is_(None)),
            )
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
