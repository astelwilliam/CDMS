from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SettingBase(BaseModel):
    key: str
    value: str
    scope: str


class SettingCreate(SettingBase):
    college_id: Optional[str] = None
    department_id: Optional[str] = None


class SettingUpdate(BaseModel):
    value: Optional[str] = None


class SettingRead(SettingBase):
    id: str
    college_id: Optional[str] = None
    department_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
