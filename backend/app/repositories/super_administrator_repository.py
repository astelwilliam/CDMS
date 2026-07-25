from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.super_administrator import SuperAdministrator
from app.repositories.base import BaseRepository


class SuperAdministratorRepository(BaseRepository[SuperAdministrator]):
    """Repository for SuperAdministrator entity."""

    def __init__(self, db: Session):
        super().__init__(SuperAdministrator, db)

    def get_by_email(self, email: str) -> Optional[SuperAdministrator]:
        stmt = select(SuperAdministrator).where(SuperAdministrator.email == email)
        return self.db.scalar(stmt)
