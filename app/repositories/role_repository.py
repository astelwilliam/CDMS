from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.role import Role
from app.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    """Repository for Role entity."""

    def __init__(self, db: Session):
        super().__init__(Role, db)

    def get_by_name(self, name: str) -> Optional[Role]:
        stmt = select(Role).where(Role.name == name)
        return self.db.scalar(stmt)
