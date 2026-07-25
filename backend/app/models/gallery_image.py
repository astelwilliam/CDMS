from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.base import TimestampMixin, SoftDeleteMixin


class GalleryImage(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "gallery_images"

    id = Column(String(36), primary_key=True, index=True)
    gallery_album_id = Column(String(36), ForeignKey("gallery_albums.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    image_reference = Column(String(500), nullable=False)

    # Relationships
    album = relationship("GalleryAlbum", back_populates="images")
    events = relationship(
        "Event",
        secondary="event_gallery_images",
        back_populates="gallery_images"
    )
