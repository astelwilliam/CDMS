from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.deps.database import get_db
from app.api.schemas.event import EventCreate, EventUpdate, EventRead
from app.repositories.event_repository import EventRepository

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("/", response_model=List[EventRead])
def get_all_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    repo = EventRepository(db)
    return repo.get_all(skip=skip, limit=limit)


@router.get("/{event_id}", response_model=EventRead)
def get_event(event_id: str, db: Session = Depends(get_db)):
    repo = EventRepository(db)
    event = repo.get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("/", response_model=EventRead, status_code=status.HTTP_201_CREATED)
def create_event(event_in: EventCreate, db: Session = Depends(get_db)):
    repo = EventRepository(db)
    return repo.create(event_in.model_dump())


@router.put("/{event_id}", response_model=EventRead)
def update_event(event_id: str, event_in: EventUpdate, db: Session = Depends(get_db)):
    repo = EventRepository(db)
    event = repo.get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return repo.update(event, event_in.model_dump(exclude_unset=True))


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: str, db: Session = Depends(get_db)):
    repo = EventRepository(db)
    if not repo.delete(event_id):
        raise HTTPException(status_code=404, detail="Event not found")
