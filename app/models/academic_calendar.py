from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.base import TimestampMixin, SoftDeleteMixin


class AcademicCalendar(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "academic_calendars"

    id = Column(String(36), primary_key=True, index=True)
    department_id = Column(String(36), ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    academic_year_or_term = Column(String(255), nullable=True)
    lifecycle_status = Column(String(50), nullable=False, default="Draft", index=True)

    # Relationships
    department = relationship("Department", back_populates="academic_calendars")
