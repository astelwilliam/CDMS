from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.setting import Setting
from app.repositories.base import BaseRepository


class SettingRepository(BaseRepository[Setting]):
    """Repository for Setting entity."""

    def __init__(self, db: Session):
        super().__init__(Setting, db)

    def get_by_key_and_scope(self, key: str, scope: str, scope_id: Optional[str] = None) -> Optional[Setting]:
        """Get a setting by key and scope."""
        stmt = select(Setting).where(Setting.key == key, Setting.scope == scope)
        if scope == "department" and scope_id:
            stmt = stmt.where(Setting.department_id == scope_id)
        elif scope == "college" and scope_id:
            stmt = stmt.where(Setting.college_id == scope_id)
        return self.db.scalar(stmt)

    def get_by_scope(self, scope: str, scope_id: Optional[str] = None) -> List[Setting]:
        stmt = select(Setting).where(Setting.scope == scope)
        if scope == "department" and scope_id:
            stmt = stmt.where(Setting.department_id == scope_id)
        elif scope == "college" and scope_id:
            stmt = stmt.where(Setting.college_id == scope_id)
        return list(self.db.scalars(stmt).all())
