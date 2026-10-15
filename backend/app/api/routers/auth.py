from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps.database import get_db
from app.api.deps.auth import get_current_auth_session, get_current_user

from app.api.schemas.auth import (
    LoginRequest,
    Token,
    CurrentUser,
    PasswordChangeRequest,
    PersistentSession,
)

from app.services.auth_service import AuthService
from app.services.session_service import (
    ResolvedSession,
    create_session,
    revoke_session,
)
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Authenticate user using form data and return access token."""
    login_data = LoginRequest(email=form_data.username, password=form_data.password)
    auth_service = AuthService(db)
    return auth_service.authenticate_user(login_data)


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=token,
        max_age=settings.SESSION_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite=settings.SESSION_COOKIE_SAMESITE,
        path="/",
    )


def _clear_session_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.SESSION_COOKIE_NAME,
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite=settings.SESSION_COOKIE_SAMESITE,
        path="/",
    )


@router.post("/session/login", response_model=PersistentSession)
def session_login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Create a revocable browser session for an authorized administrator."""
    login_data = LoginRequest(email=form_data.username, password=form_data.password)
    user = AuthService(db).authenticate_credentials(login_data)
    if user.role not in {"super_admin", "department_admin"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access unavailable",
        )
    created = create_session(db, user.id)
    _set_session_cookie(response, created.token)
    return PersistentSession(
        user=CurrentUser.model_validate(user),
        csrf_token=created.csrf_token,
    )


@router.get("/session", response_model=PersistentSession)
def restore_session(
    resolved: ResolvedSession = Depends(get_current_auth_session),
):
    """Restore a valid browser session after a page reload."""
    return PersistentSession(
        user=CurrentUser.model_validate(resolved.user),
        csrf_token=resolved.csrf_token,
    )


@router.post("/session/logout", status_code=status.HTTP_204_NO_CONTENT)
def session_logout(
    response: Response,
    resolved: ResolvedSession = Depends(get_current_auth_session),
    db: Session = Depends(get_db),
):
    """Revoke the current browser session and remove its cookie."""
    revoke_session(db, resolved.session)
    response.status_code = status.HTTP_204_NO_CONTENT
    _clear_session_cookie(response)
    return response


@router.get("/me", response_model=CurrentUser)
def get_me(current_user: CurrentUser = Depends(get_current_user)):
    """Return the currently authenticated user."""
    return current_user


@router.post("/change-password")
def change_password(
    password_data: PasswordChangeRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change the password of the currently logged-in user."""
    auth_service = AuthService(db)
    success = auth_service.change_password(
        current_user.id,
        password_data.current_password,
        password_data.new_password
    )
    if success:
        return {"message": "Password changed successfully"}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Failed to change password"
    )
