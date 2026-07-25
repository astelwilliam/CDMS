from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.deps.database import get_db
from app.api.schemas.audit_log import AuditLogRead
from app.repositories.audit_log_repository import AuditLogRepository

router = APIRouter(prefix="/audit_logs", tags=["Audit Logs"])


@router.get("/", response_model=List[AuditLogRead])
def get_all_audit_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    repo = AuditLogRepository(db)
    return repo.get_all(skip=skip, limit=limit)


@router.get("/{log_id}", response_model=AuditLogRead)
def get_audit_log(log_id: str, db: Session = Depends(get_db)):
    repo = AuditLogRepository(db)
    log = repo.get(log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return log
