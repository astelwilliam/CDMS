from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.faculty_member import FacultyMember
from app.repositories.base import BaseRepository


class FacultyMemberRepository(BaseRepository[FacultyMember]):
    """Repository for FacultyMember entity."""

    def __init__(self, db: Session):
        super().__init__(FacultyMember, db)

    def get_by_department(self, department_id: str, skip: int = 0, limit: int = 100) -> List[FacultyMember]:
        """Get all active faculty members in a department."""
        stmt = (
            select(FacultyMember)
            .where(FacultyMember.department_id == department_id, FacultyMember.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
