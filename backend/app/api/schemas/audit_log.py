from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AuditLogRead(BaseModel):
    id: str
    action_type: str
    timestamp: datetime
    performed_by_id: str
    affected_object_reference: Optional[str] = None
    additional_details: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
