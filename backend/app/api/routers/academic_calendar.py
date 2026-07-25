from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.deps.database import get_db
from app.api.schemas.academic_calendar import AcademicCalendarCreate, AcademicCalendarUpdate, AcademicCalendarRead
from app.repositories.academic_calendar_repository import AcademicCalendarRepository

router = APIRouter(prefix="/academic_calendars", tags=["Academic Calendars"])


@router.get("/", response_model=List[AcademicCalendarRead])
def get_all_calendars(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    repo = AcademicCalendarRepository(db)
    return repo.get_all(skip=skip, limit=limit)


@router.get("/{calendar_id}", response_model=AcademicCalendarRead)
def get_calendar(calendar_id: str, db: Session = Depends(get_db)):
    repo = AcademicCalendarRepository(db)
    calendar = repo.get(calendar_id)
    if not calendar:
        raise HTTPException(status_code=404, detail="Academic calendar not found")
    return calendar


@router.post("/", response_model=AcademicCalendarRead, status_code=status.HTTP_201_CREATED)
def create_calendar(calendar_in: AcademicCalendarCreate, db: Session = Depends(get_db)):
    repo = AcademicCalendarRepository(db)
    return repo.create(calendar_in.model_dump())


@router.put("/{calendar_id}", response_model=AcademicCalendarRead)
def update_calendar(calendar_id: str, calendar_in: AcademicCalendarUpdate, db: Session = Depends(get_db)):
    repo = AcademicCalendarRepository(db)
    calendar = repo.get(calendar_id)
    if not calendar:
        raise HTTPException(status_code=404, detail="Academic calendar not found")
    return repo.update(calendar, calendar_in.model_dump(exclude_unset=True))


@router.delete("/{calendar_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calendar(calendar_id: str, db: Session = Depends(get_db)):
    repo = AcademicCalendarRepository(db)
    if not repo.delete(calendar_id):
        raise HTTPException(status_code=404, detail="Academic calendar not found")
