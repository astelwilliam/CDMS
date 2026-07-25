from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class DepartmentAdministratorBase(BaseModel):
    name: str
    email: EmailStr


class DepartmentAdministratorCreate(DepartmentAdministratorBase):
    role_id: str


class DepartmentAdministratorUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role_id: Optional[str] = None


class DepartmentAdministratorRead(DepartmentAdministratorBase):
    id: str
    role_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
