import uuid
from sqlalchemy import Column, String, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.base import TimestampMixin


class Setting(Base, TimestampMixin):
    __tablename__ = "settings"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    college_id = Column(String(36), ForeignKey("colleges.id", ondelete="CASCADE"), nullable=True, index=True)
    department_id = Column(String(36), ForeignKey("departments.id", ondelete="CASCADE"), nullable=True, index=True)
    key = Column(String(255), nullable=False, index=True)
    value = Column(Text, nullable=False)
    scope = Column(String(50), nullable=False)

    __table_args__ = (
        CheckConstraint("scope IN ('college', 'department')", name="ck_setting_scope"),
    )

    # Relationships
    college = relationship("College", back_populates="settings")
    department = relationship("Department", back_populates="settings")
