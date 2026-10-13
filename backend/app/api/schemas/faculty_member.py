from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class FacultyMemberBase(BaseModel):
    name: str
    title: Optional[str] = None
    biography: Optional[str] = None
    contact_information: Optional[str] = None
    profile_image_reference: Optional[str] = None


class FacultyMemberCreate(FacultyMemberBase):
    model_config = ConfigDict(extra="forbid")

    department_id: str


class FacultyMemberUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Optional[str] = None
    title: Optional[str] = None
    biography: Optional[str] = None
    contact_information: Optional[str] = None
    profile_image_reference: Optional[str] = None


class FacultyMemberRead(FacultyMemberBase):
    id: str
    department_id: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
