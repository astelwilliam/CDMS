from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.deps.database import get_db
from app.api.schemas.college import CollegeCreate, CollegeUpdate, CollegeRead
from app.repositories.college_repository import CollegeRepository
from app.services.administrative_deletion import (
    AdministrativeDeletionDisabled,
    DELETION_DISABLED_DETAIL,
)

router = APIRouter(prefix="/colleges", tags=["Colleges"])


@router.get("/", response_model=List[CollegeRead])
def get_all_colleges(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    repo = CollegeRepository(db)
    return repo.get_all(skip=skip, limit=limit)


@router.get("/{college_id}", response_model=CollegeRead)
def get_college(college_id: str, db: Session = Depends(get_db)):
    repo = CollegeRepository(db)
    college = repo.get(college_id)
    if not college:
        raise HTTPException(status_code=404, detail="College not found")
    return college


@router.post("/", response_model=CollegeRead, status_code=status.HTTP_201_CREATED)
def create_college(college_in: CollegeCreate, db: Session = Depends(get_db)):
    repo = CollegeRepository(db)
    return repo.create(college_in.model_dump())


@router.put("/{college_id}", response_model=CollegeRead)
def update_college(college_id: str, college_in: CollegeUpdate, db: Session = Depends(get_db)):
    repo = CollegeRepository(db)
    college = repo.get(college_id)
    if not college:
        raise HTTPException(status_code=404, detail="College not found")
    return repo.update(college, college_in.model_dump(exclude_unset=True))


@router.delete("/{college_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_college(college_id: str, db: Session = Depends(get_db)):
    repo = CollegeRepository(db)
    try:
        repo.delete(college_id)
    except AdministrativeDeletionDisabled as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=DELETION_DISABLED_DETAIL,
        ) from exc
