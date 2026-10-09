import uuid
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.base import TimestampMixin, SoftDeleteMixin


class FacultyMember(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "faculty_members"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    department_id = Column(String(36), ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    title = Column(String(255), nullable=True)
    biography = Column(Text, nullable=True)
    contact_information = Column(Text, nullable=True)
    profile_image_reference = Column(String(500), nullable=True)

    # Relationships
    department = relationship("Department", back_populates="faculty_members")
