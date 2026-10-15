from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.api.schemas.auth import Token, CurrentUser, LoginRequest
from app.core.security import verify_password, create_access_token, hash_password
from app.core.config import settings


class AuthService:
    """Service responsible for authentication business logic."""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def authenticate_credentials(self, login_data: LoginRequest) -> User:
        user = self.user_repo.get_by_email(login_data.email)
        
        if (
            not user
            or not verify_password(login_data.password, user.hashed_password)
            or not user.is_active
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    def authenticate_user(self, login_data: LoginRequest) -> Token:
        """Authenticate user credentials and return a bearer access token."""
        user = self.authenticate_credentials(login_data)
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.id, "email": user.email, "role": user.role},
            expires_delta=access_token_expires
        )

        return Token(access_token=access_token, token_type="bearer")

    def get_current_user(self, user_id: str) -> CurrentUser:
        """
        Retrieve the current authenticated user.
        """
        user = self.user_repo.get(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return CurrentUser.model_validate(user)

    def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """
        Change user password after verifying current password.
        """
        user = self.user_repo.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Hash and update new password
        user.hashed_password = hash_password(new_password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return True
