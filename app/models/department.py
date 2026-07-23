from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.base import TimestampMixin, SoftDeleteMixin


class Department(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "departments"

    id = Column(String(36), primary_key=True, index=True)
    college_id = Column(String(36), ForeignKey("colleges.id", ondelete="RESTRICT"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    contact_information = Column(Text, nullable=True)

    # Relationships
    college = relationship("College", back_populates="departments")
    faculty_members = relationship("FacultyMember", back_populates="department", cascade="all, delete-orphan")
    announcements = relationship("Announcement", back_populates="department")
    events = relationship("Event", back_populates="department", cascade="all, delete-orphan")
    academic_resources = relationship("AcademicResource", back_populates="department", cascade="all, delete-orphan")
    timetables = relationship("Timetable", back_populates="department", cascade="all, delete-orphan")
    gallery_albums = relationship("GalleryAlbum", back_populates="department", cascade="all, delete-orphan")
    academic_calendars = relationship("AcademicCalendar", back_populates="department", cascade="all, delete-orphan")
    help_center_articles = relationship("HelpCenterArticle", back_populates="department", cascade="all, delete-orphan")
    settings = relationship("Setting", back_populates="department", cascade="all, delete-orphan")
