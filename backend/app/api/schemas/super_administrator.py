from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class SuperAdministratorBase(BaseModel):
    name: str
    email: EmailStr


class SuperAdministratorCreate(SuperAdministratorBase):
    role_id: str


class SuperAdministratorUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role_id: Optional[str] = None


class SuperAdministratorRead(SuperAdministratorBase):
    id: str
    role_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
