from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.base import TimestampMixin, SoftDeleteMixin


class Announcement(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "announcements"

    id = Column(String(36), primary_key=True, index=True)
    department_id = Column(String(36), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True)
    college_id = Column(String(36), ForeignKey("colleges.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    publication_date = Column(DateTime(timezone=True), nullable=True)
    expiration_date = Column(DateTime(timezone=True), nullable=True)
    lifecycle_status = Column(String(50), nullable=False, default="Draft", index=True)

    # Relationships
    department = relationship("Department", back_populates="announcements")
    college = relationship("College", back_populates="announcements")
