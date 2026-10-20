from collections.abc import Collection

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.department import Department
from app.repositories.base import BaseRepository
from app.services.administrative_deletion import AdministrativeDeletionDisabled


class DepartmentRepository(BaseRepository[Department]):
    def __init__(self, db: Session):
        super().__init__(Department, db)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Department]:
        stmt = select(Department).order_by(Department.id).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def delete(self, id: str) -> bool:
        raise AdministrativeDeletionDisabled

    def get_assigned(
        self,
        department_ids: Collection[str],
        skip: int = 0,
        limit: int = 100,
    ) -> list[Department]:
        return list(
            self.db.scalars(
                select(Department)
                .where(
                    Department.id.in_(department_ids),
                    Department.deleted_at.is_(None),
                )
                .order_by(Department.id)
                .offset(skip)
                .limit(limit)
            )
        )

    def get_assigned_by_id(
        self,
        department_id: str,
        department_ids: Collection[str],
    ) -> Department | None:
        return self.db.scalar(
            select(Department).where(
                Department.id == department_id,
                Department.id.in_(department_ids),
                Department.deleted_at.is_(None),
            )
        )
