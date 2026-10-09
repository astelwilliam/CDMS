import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import mapped_column, relationship

from app.db.session import Base
from app.models.base import TimestampMixin, SoftDeleteMixin


class Department(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "departments"

    id = mapped_column(
        String(36),
        primary_key=True,
        index=True,
        default=lambda: str(uuid.uuid4()),
    )
    college_id = mapped_column(
        String(36),
        ForeignKey("colleges.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    name = mapped_column(String(255), nullable=False, index=True)
    description = mapped_column(Text, nullable=True)
    contact_information = mapped_column(Text, nullable=True)

    # Relationships
    college = relationship("College", back_populates="departments")
    administrators = relationship(
        "DepartmentAdministrator",
        secondary="department_administrator_departments",
        back_populates="departments",
    )
    faculty_members = relationship("FacultyMember", back_populates="department", cascade="all, delete-orphan")
    announcements = relationship("Announcement", back_populates="department")
    events = relationship("Event", back_populates="department", cascade="all, delete-orphan")
    academic_resources = relationship("AcademicResource", back_populates="department", cascade="all, delete-orphan")
    timetables = relationship("Timetable", back_populates="department", cascade="all, delete-orphan")
    gallery_albums = relationship("GalleryAlbum", back_populates="department", cascade="all, delete-orphan")
    academic_calendars = relationship("AcademicCalendar", back_populates="department", cascade="all, delete-orphan")
    help_center_articles = relationship("HelpCenterArticle", back_populates="department", cascade="all, delete-orphan")
    settings = relationship("Setting", back_populates="department", cascade="all, delete-orphan")
