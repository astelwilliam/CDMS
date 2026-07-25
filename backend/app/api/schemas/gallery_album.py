from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class GalleryAlbumBase(BaseModel):
    title: str
    description: Optional[str] = None
    lifecycle_status: str = "Draft"


class GalleryAlbumCreate(GalleryAlbumBase):
    department_id: str


class GalleryAlbumUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    lifecycle_status: Optional[str] = None


class GalleryAlbumRead(GalleryAlbumBase):
    id: str
    department_id: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
