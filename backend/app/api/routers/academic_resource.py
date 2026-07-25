from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.deps.database import get_db
from app.api.schemas.academic_resource import AcademicResourceCreate, AcademicResourceUpdate, AcademicResourceRead
from app.repositories.academic_resource_repository import AcademicResourceRepository

router = APIRouter(prefix="/academic_resources", tags=["Academic Resources"])


@router.get("/", response_model=List[AcademicResourceRead])
def get_all_resources(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    repo = AcademicResourceRepository(db)
    return repo.get_all(skip=skip, limit=limit)


@router.get("/{resource_id}", response_model=AcademicResourceRead)
def get_resource(resource_id: str, db: Session = Depends(get_db)):
    repo = AcademicResourceRepository(db)
    resource = repo.get(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource


@router.post("/", response_model=AcademicResourceRead, status_code=status.HTTP_201_CREATED)
def create_resource(resource_in: AcademicResourceCreate, db: Session = Depends(get_db)):
    repo = AcademicResourceRepository(db)
    return repo.create(resource_in.model_dump())


@router.put("/{resource_id}", response_model=AcademicResourceRead)
def update_resource(resource_id: str, resource_in: AcademicResourceUpdate, db: Session = Depends(get_db)):
    repo = AcademicResourceRepository(db)
    resource = repo.get(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return repo.update(resource, resource_in.model_dump(exclude_unset=True))


@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource(resource_id: str, db: Session = Depends(get_db)):
    repo = AcademicResourceRepository(db)
    if not repo.delete(resource_id):
        raise HTTPException(status_code=404, detail="Resource not found")
