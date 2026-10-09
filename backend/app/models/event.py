import uuid
from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.base import TimestampMixin, SoftDeleteMixin


class Event(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "events"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    department_id = Column(String(36), ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    date_and_time = Column(DateTime(timezone=True), nullable=True)
    location = Column(String(255), nullable=True)
    lifecycle_status = Column(String(50), nullable=False, default="Draft", index=True)

    # Relationships
    department = relationship("Department", back_populates="events")
    gallery_images = relationship(
        "GalleryImage",
        secondary="event_gallery_images",
        back_populates="events"
    )
