from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    date_and_time: Optional[datetime] = None
    location: Optional[str] = None
    lifecycle_status: str = "Draft"


class EventCreate(EventBase):
    department_id: str


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date_and_time: Optional[datetime] = None
    location: Optional[str] = None
    lifecycle_status: Optional[str] = None


class EventRead(EventBase):
    id: str
    department_id: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
