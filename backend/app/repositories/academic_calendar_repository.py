from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.academic_calendar import AcademicCalendar
from app.repositories.base import BaseRepository


class AcademicCalendarRepository(BaseRepository[AcademicCalendar]):
    """Repository for AcademicCalendar entity."""

    def __init__(self, db: Session):
        super().__init__(AcademicCalendar, db)

    def get_by_department(self, department_id: str, skip: int = 0, limit: int = 100) -> List[AcademicCalendar]:
        stmt = (
            select(AcademicCalendar)
            .where(AcademicCalendar.department_id == department_id, AcademicCalendar.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
