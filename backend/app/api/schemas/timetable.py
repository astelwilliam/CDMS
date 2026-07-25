from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TimetableBase(BaseModel):
    title: str
    description: Optional[str] = None
    schedule_period: Optional[str] = None
    lifecycle_status: str = "Draft"


class TimetableCreate(TimetableBase):
    department_id: str


class TimetableUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    schedule_period: Optional[str] = None
    lifecycle_status: Optional[str] = None


class TimetableRead(TimetableBase):
    id: str
    department_id: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
