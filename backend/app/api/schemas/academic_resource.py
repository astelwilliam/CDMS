from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AcademicResourceBase(BaseModel):
    title: str
    description: Optional[str] = None
    file_reference_or_link: Optional[str] = None
    lifecycle_status: str = "Draft"


class AcademicResourceCreate(AcademicResourceBase):
    department_id: str


class AcademicResourceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    file_reference_or_link: Optional[str] = None
    lifecycle_status: Optional[str] = None


class AcademicResourceRead(AcademicResourceBase):
    id: str
    department_id: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
