from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AnnouncementBase(BaseModel):
    title: str
    content: str
    publication_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    lifecycle_status: str = "Draft"


class AnnouncementCreate(AnnouncementBase):
    department_id: Optional[str] = None
    college_id: Optional[str] = None


class AnnouncementUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    publication_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    lifecycle_status: Optional[str] = None


class AnnouncementRead(AnnouncementBase):
    id: str
    department_id: Optional[str] = None
    college_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
