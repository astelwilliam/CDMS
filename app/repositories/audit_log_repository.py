from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.audit_log import AuditLog
from app.repositories.base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    """Repository for AuditLog entity."""

    def __init__(self, db: Session):
        super().__init__(AuditLog, db)

    def get_by_performed_by(self, performed_by_id: str, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        stmt = (
            select(AuditLog)
            .where(AuditLog.performed_by_id == performed_by_id)
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
