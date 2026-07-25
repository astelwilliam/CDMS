from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.timetable import Timetable
from app.repositories.base import BaseRepository


class TimetableRepository(BaseRepository[Timetable]):
    """Repository for Timetable entity."""

    def __init__(self, db: Session):
        super().__init__(Timetable, db)

    def get_by_department(self, department_id: str, skip: int = 0, limit: int = 100) -> List[Timetable]:
        stmt = (
            select(Timetable)
            .where(Timetable.department_id == department_id, Timetable.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
