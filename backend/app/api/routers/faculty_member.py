from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.deps.database import get_db
from app.api.schemas.faculty_member import FacultyMemberCreate, FacultyMemberUpdate, FacultyMemberRead
from app.repositories.faculty_member_repository import FacultyMemberRepository

router = APIRouter(prefix="/faculty_members", tags=["Faculty Members"])


@router.get("/", response_model=List[FacultyMemberRead])
def get_all_faculty_members(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    repo = FacultyMemberRepository(db)
    return repo.get_all(skip=skip, limit=limit)


@router.get("/{faculty_member_id}", response_model=FacultyMemberRead)
def get_faculty_member(faculty_member_id: str, db: Session = Depends(get_db)):
    repo = FacultyMemberRepository(db)
    faculty = repo.get(faculty_member_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty member not found")
    return faculty


@router.post("/", response_model=FacultyMemberRead, status_code=status.HTTP_201_CREATED)
def create_faculty_member(faculty_in: FacultyMemberCreate, db: Session = Depends(get_db)):
    repo = FacultyMemberRepository(db)
    return repo.create(faculty_in.model_dump())


@router.put("/{faculty_member_id}", response_model=FacultyMemberRead)
def update_faculty_member(faculty_member_id: str, faculty_in: FacultyMemberUpdate, db: Session = Depends(get_db)):
    repo = FacultyMemberRepository(db)
    faculty = repo.get(faculty_member_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty member not found")
    return repo.update(faculty, faculty_in.model_dump(exclude_unset=True))


@router.delete("/{faculty_member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_faculty_member(faculty_member_id: str, db: Session = Depends(get_db)):
    repo = FacultyMemberRepository(db)
    if not repo.delete(faculty_member_id):
        raise HTTPException(status_code=404, detail="Faculty member not found")
