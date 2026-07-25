from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class HelpCenterArticleBase(BaseModel):
    title: str
    content: str
    category: Optional[str] = None
    lifecycle_status: str = "Draft"


class HelpCenterArticleCreate(HelpCenterArticleBase):
    department_id: str


class HelpCenterArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    lifecycle_status: Optional[str] = None


class HelpCenterArticleRead(HelpCenterArticleBase):
    id: str
    department_id: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
