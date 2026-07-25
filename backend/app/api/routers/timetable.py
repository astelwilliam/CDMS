from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.deps.database import get_db
from app.api.schemas.timetable import TimetableCreate, TimetableUpdate, TimetableRead
from app.repositories.timetable_repository import TimetableRepository

router = APIRouter(prefix="/timetables", tags=["Timetables"])


@router.get("/", response_model=List[TimetableRead])
def get_all_timetables(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    repo = TimetableRepository(db)
    return repo.get_all(skip=skip, limit=limit)


@router.get("/{timetable_id}", response_model=TimetableRead)
def get_timetable(timetable_id: str, db: Session = Depends(get_db)):
    repo = TimetableRepository(db)
    timetable = repo.get(timetable_id)
    if not timetable:
        raise HTTPException(status_code=404, detail="Timetable not found")
    return timetable


@router.post("/", response_model=TimetableRead, status_code=status.HTTP_201_CREATED)
def create_timetable(timetable_in: TimetableCreate, db: Session = Depends(get_db)):
    repo = TimetableRepository(db)
    return repo.create(timetable_in.model_dump())


@router.put("/{timetable_id}", response_model=TimetableRead)
def update_timetable(timetable_id: str, timetable_in: TimetableUpdate, db: Session = Depends(get_db)):
    repo = TimetableRepository(db)
    timetable = repo.get(timetable_id)
    if not timetable:
        raise HTTPException(status_code=404, detail="Timetable not found")
    return repo.update(timetable, timetable_in.model_dump(exclude_unset=True))


@router.delete("/{timetable_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_timetable(timetable_id: str, db: Session = Depends(get_db)):
    repo = TimetableRepository(db)
    if not repo.delete(timetable_id):
        raise HTTPException(status_code=404, detail="Timetable not found")
