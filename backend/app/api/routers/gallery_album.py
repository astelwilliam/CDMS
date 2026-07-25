from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.deps.database import get_db
from app.api.schemas.gallery_album import GalleryAlbumCreate, GalleryAlbumUpdate, GalleryAlbumRead
from app.repositories.gallery_album_repository import GalleryAlbumRepository

router = APIRouter(prefix="/gallery_albums", tags=["Gallery Albums"])


@router.get("/", response_model=List[GalleryAlbumRead])
def get_all_albums(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    repo = GalleryAlbumRepository(db)
    return repo.get_all(skip=skip, limit=limit)


@router.get("/{album_id}", response_model=GalleryAlbumRead)
def get_album(album_id: str, db: Session = Depends(get_db)):
    repo = GalleryAlbumRepository(db)
    album = repo.get(album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Gallery album not found")
    return album


@router.post("/", response_model=GalleryAlbumRead, status_code=status.HTTP_201_CREATED)
def create_album(album_in: GalleryAlbumCreate, db: Session = Depends(get_db)):
    repo = GalleryAlbumRepository(db)
    return repo.create(album_in.model_dump())


@router.put("/{album_id}", response_model=GalleryAlbumRead)
def update_album(album_id: str, album_in: GalleryAlbumUpdate, db: Session = Depends(get_db)):
    repo = GalleryAlbumRepository(db)
    album = repo.get(album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Gallery album not found")
    return repo.update(album, album_in.model_dump(exclude_unset=True))


@router.delete("/{album_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_album(album_id: str, db: Session = Depends(get_db)):
    repo = GalleryAlbumRepository(db)
    if not repo.delete(album_id):
        raise HTTPException(status_code=404, detail="Gallery album not found")
