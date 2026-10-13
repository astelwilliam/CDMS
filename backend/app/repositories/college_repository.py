from sqlalchemy.orm import Session

from app.models.college import College
from app.repositories.base import BaseRepository
from app.services.administrative_deletion import AdministrativeDeletionDisabled


class CollegeRepository(BaseRepository[College]):
    def __init__(self, db: Session):
        super().__init__(College, db)

    def delete(self, id: str) -> bool:
        raise AdministrativeDeletionDisabled
