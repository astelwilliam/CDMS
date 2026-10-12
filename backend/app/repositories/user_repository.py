from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User entity with authentication-specific methods."""

    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by email address."""
        stmt = select(User).where(User.email == email)
        return self.db.scalar(stmt)

    def exists_by_email(self, email: str) -> bool:
        """Check if a user with the given email already exists."""
        stmt = select(User.id).where(User.email == email)
        return self.db.scalar(stmt) is not None

    def update(self, db_obj: User, obj_in: dict) -> User:
        if {"role", "is_active"} & obj_in.keys():
            raise ValueError(
                "Use the privileged user mutation service for authorization fields"
            )
        return super().update(db_obj, obj_in)
