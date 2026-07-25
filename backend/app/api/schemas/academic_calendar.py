from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AcademicCalendarBase(BaseModel):
    title: str
    description: Optional[str] = None
    academic_year_or_term: Optional[str] = None
    lifecycle_status: str = "Draft"


class AcademicCalendarCreate(AcademicCalendarBase):
    department_id: str


class AcademicCalendarUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    academic_year_or_term: Optional[str] = None
    lifecycle_status: Optional[str] = None


class AcademicCalendarRead(AcademicCalendarBase):
    id: str
    department_id: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
