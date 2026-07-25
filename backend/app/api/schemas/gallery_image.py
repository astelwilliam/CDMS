from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class GalleryImageBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    image_reference: str


class GalleryImageCreate(GalleryImageBase):
    gallery_album_id: str


class GalleryImageUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    image_reference: Optional[str] = None


class GalleryImageRead(GalleryImageBase):
    id: str
    gallery_album_id: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
