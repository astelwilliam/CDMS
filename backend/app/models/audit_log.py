import uuid
from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.base import TimestampMixin


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    action_type = Column(String(100), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    performed_by_id = Column(String(36), nullable=False, index=True)
    affected_object_reference = Column(String(255), nullable=True)
    additional_details = Column(Text, nullable=True)
