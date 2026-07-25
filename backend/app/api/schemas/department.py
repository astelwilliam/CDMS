from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DepartmentBase(BaseModel):
    name: str
    description: Optional[str] = None
    contact_information: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    college_id: str


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    contact_information: Optional[str] = None


class DepartmentRead(DepartmentBase):
    id: str
    college_id: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
