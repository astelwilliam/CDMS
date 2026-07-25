from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.help_center_article import HelpCenterArticle
from app.repositories.base import BaseRepository


class HelpCenterArticleRepository(BaseRepository[HelpCenterArticle]):
    """Repository for HelpCenterArticle entity."""

    def __init__(self, db: Session):
        super().__init__(HelpCenterArticle, db)

    def get_by_department(self, department_id: str, skip: int = 0, limit: int = 100) -> List[HelpCenterArticle]:
        stmt = (
            select(HelpCenterArticle)
            .where(HelpCenterArticle.department_id == department_id, HelpCenterArticle.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
