import uuid
from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.base import TimestampMixin


class College(Base, TimestampMixin):
    __tablename__ = "colleges"

    id = Column(
    String(36),
    primary_key=True,
    index=True,
    default=lambda: str(uuid.uuid4())
    )
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    contact_information = Column(Text, nullable=True)
    logo_reference = Column(String(500), nullable=True)

    # Relationships
    departments = relationship("Department", back_populates="college", cascade="all, delete-orphan")
    announcements = relationship("Announcement", back_populates="college")
    settings = relationship("Setting", back_populates="college", cascade="all, delete-orphan")
