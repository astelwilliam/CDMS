from collections.abc import Collection
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.department import Department
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

    def get_assigned(
        self,
        department_ids: Collection[str],
        skip: int = 0,
        limit: int = 100,
    ) -> list[FacultyMember]:
        stmt = (
            select(FacultyMember)
            .join(Department, Department.id == FacultyMember.department_id)
            .where(
                FacultyMember.department_id.in_(department_ids),
                FacultyMember.deleted_at.is_(None),
                Department.deleted_at.is_(None),
            )
            .order_by(FacultyMember.id)
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_assigned_by_id(
        self,
        faculty_member_id: str,
        department_ids: Collection[str],
    ) -> FacultyMember | None:
        return self.db.scalar(
            select(FacultyMember)
            .join(Department, Department.id == FacultyMember.department_id)
            .where(
                FacultyMember.id == faculty_member_id,
                FacultyMember.department_id.in_(department_ids),
                FacultyMember.deleted_at.is_(None),
                Department.deleted_at.is_(None),
            )
        )
