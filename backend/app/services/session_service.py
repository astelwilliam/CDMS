import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.auth_session import AuthSession
from app.models.user import User


@dataclass(frozen=True)
class CreatedSession:
    session: AuthSession
    token: str
    csrf_token: str


@dataclass(frozen=True)
class ResolvedSession:
    session: AuthSession
    user: User
    csrf_token: str


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def csrf_token_for_session(token: str) -> str:
    return hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        f"cdms-csrf:{token}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def create_session(db: Session, user_id: str) -> CreatedSession:
    token = secrets.token_urlsafe(48)
    session = AuthSession(
        user_id=user_id,
        token_hash=hash_session_token(token),
        expires_at=_utc_now() + timedelta(minutes=settings.SESSION_EXPIRE_MINUTES),
    )
    try:
        db.add(session)
        db.commit()
        db.refresh(session)
    except Exception:
        db.rollback()
        raise
    return CreatedSession(
        session=session,
        token=token,
        csrf_token=csrf_token_for_session(token),
    )


def resolve_session(db: Session, token: str) -> ResolvedSession | None:
    if not token:
        return None
    session = db.scalar(
        select(AuthSession).where(
            AuthSession.token_hash == hash_session_token(token),
        )
    )
    if (
        session is None
        or session.revoked_at is not None
        or _as_utc(session.expires_at) <= _utc_now()
    ):
        return None
    user = db.get(User, session.user_id)
    if (
        user is None
        or not user.is_active
        or user.role not in {"super_admin", "department_admin"}
    ):
        return None
    return ResolvedSession(
        session=session,
        user=user,
        csrf_token=csrf_token_for_session(token),
    )


def revoke_session(db: Session, session: AuthSession) -> None:
    session.revoked_at = _utc_now()
    try:
        db.add(session)
        db.commit()
    except Exception:
        db.rollback()
        raise


def csrf_token_matches(session_token: str, supplied_token: str | None) -> bool:
    if not session_token or not supplied_token:
        return False
    return secrets.compare_digest(
        csrf_token_for_session(session_token),
        supplied_token,
    )
