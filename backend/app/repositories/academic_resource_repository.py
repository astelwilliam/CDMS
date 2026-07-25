from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.academic_resource import AcademicResource
from app.repositories.base import BaseRepository


class AcademicResourceRepository(BaseRepository[AcademicResource]):
    """Repository for AcademicResource entity."""

    def __init__(self, db: Session):
        super().__init__(AcademicResource, db)

    def get_by_department(self, department_id: str, skip: int = 0, limit: int = 100) -> List[AcademicResource]:
        stmt = (
            select(AcademicResource)
            .where(AcademicResource.department_id == department_id, AcademicResource.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
