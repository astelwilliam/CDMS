from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.deps.database import get_db
from app.api.schemas.gallery_image import GalleryImageCreate, GalleryImageUpdate, GalleryImageRead
from app.repositories.gallery_image_repository import GalleryImageRepository

router = APIRouter(prefix="/gallery_images", tags=["Gallery Images"])


@router.get("/", response_model=List[GalleryImageRead])
def get_all_images(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    repo = GalleryImageRepository(db)
    return repo.get_all(skip=skip, limit=limit)


@router.get("/{image_id}", response_model=GalleryImageRead)
def get_image(image_id: str, db: Session = Depends(get_db)):
    repo = GalleryImageRepository(db)
    image = repo.get(image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Gallery image not found")
    return image


@router.post("/", response_model=GalleryImageRead, status_code=status.HTTP_201_CREATED)
def create_image(image_in: GalleryImageCreate, db: Session = Depends(get_db)):
    repo = GalleryImageRepository(db)
    return repo.create(image_in.model_dump())


@router.put("/{image_id}", response_model=GalleryImageRead)
def update_image(image_id: str, image_in: GalleryImageUpdate, db: Session = Depends(get_db)):
    repo = GalleryImageRepository(db)
    image = repo.get(image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Gallery image not found")
    return repo.update(image, image_in.model_dump(exclude_unset=True))


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_image(image_id: str, db: Session = Depends(get_db)):
    repo = GalleryImageRepository(db)
    if not repo.delete(image_id):
        raise HTTPException(status_code=404, detail="Gallery image not found")
