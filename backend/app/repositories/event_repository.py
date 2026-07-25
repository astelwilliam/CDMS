from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.event import Event
from app.repositories.base import BaseRepository


class EventRepository(BaseRepository[Event]):
    """Repository for Event entity."""

    def __init__(self, db: Session):
        super().__init__(Event, db)

    def get_by_department(self, department_id: str, skip: int = 0, limit: int = 100) -> List[Event]:
        stmt = (
            select(Event)
            .where(Event.department_id == department_id, Event.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
