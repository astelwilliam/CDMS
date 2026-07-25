from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CollegeBase(BaseModel):
    name: str
    description: Optional[str] = None
    contact_information: Optional[str] = None
    logo_reference: Optional[str] = None


class CollegeCreate(CollegeBase):
    pass


class CollegeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    contact_information: Optional[str] = None
    logo_reference: Optional[str] = None


class CollegeRead(CollegeBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
