from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.deps.database import get_db
from app.api.schemas.help_center_article import HelpCenterArticleCreate, HelpCenterArticleUpdate, HelpCenterArticleRead
from app.repositories.help_center_article_repository import HelpCenterArticleRepository

router = APIRouter(prefix="/help_center_articles", tags=["Help Center Articles"])


@router.get("/", response_model=List[HelpCenterArticleRead])
def get_all_articles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    repo = HelpCenterArticleRepository(db)
    return repo.get_all(skip=skip, limit=limit)


@router.get("/{article_id}", response_model=HelpCenterArticleRead)
def get_article(article_id: str, db: Session = Depends(get_db)):
    repo = HelpCenterArticleRepository(db)
    article = repo.get(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Help center article not found")
    return article


@router.post("/", response_model=HelpCenterArticleRead, status_code=status.HTTP_201_CREATED)
def create_article(article_in: HelpCenterArticleCreate, db: Session = Depends(get_db)):
    repo = HelpCenterArticleRepository(db)
    return repo.create(article_in.model_dump())


@router.put("/{article_id}", response_model=HelpCenterArticleRead)
def update_article(article_id: str, article_in: HelpCenterArticleUpdate, db: Session = Depends(get_db)):
    repo = HelpCenterArticleRepository(db)
    article = repo.get(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Help center article not found")
    return repo.update(article, article_in.model_dump(exclude_unset=True))


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(article_id: str, db: Session = Depends(get_db)):
    repo = HelpCenterArticleRepository(db)
    if not repo.delete(article_id):
        raise HTTPException(status_code=404, detail="Help center article not found")
