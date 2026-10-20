from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.college import College
from app.repositories.base import BaseRepository
from app.services.administrative_deletion import AdministrativeDeletionDisabled


class CollegeRepository(BaseRepository[College]):
    def __init__(self, db: Session):
        super().__init__(College, db)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[College]:
        stmt = select(College).order_by(College.id).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def delete(self, id: str) -> bool:
        raise AdministrativeDeletionDisabled
