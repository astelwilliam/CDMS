from sqlalchemy import func, select, text
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.api.schemas.auth import LoginRequest
from app.core.security import hash_password
from app.models.user import User


class AdministratorAlreadyProvisioned(Exception):
    """A super-administrator login identity already exists."""


class AdministratorEmailUnavailable(Exception):
    """The requested email already belongs to another login identity."""


class InvalidAdministratorCredentials(Exception):
    """The supplied bootstrap credentials do not satisfy validation rules."""


def has_super_administrator(db: Session) -> bool:
    """Return whether any authenticated super-administrator identity exists."""
    return db.scalar(
        select(User.id).where(User.role == "super_admin").limit(1)
    ) is not None


def _lock_user_table_for_bootstrap(db: Session) -> None:
    """Serialize initial-user provisioning when running on PostgreSQL."""
    if db.get_bind().dialect.name == "postgresql":
        db.execute(text("LOCK TABLE users IN SHARE ROW EXCLUSIVE MODE"))


def stage_initial_super_administrator(
    db: Session,
    email: str,
    password: str,
) -> User:
    """Stage the first super-admin identity without committing or rolling back."""
    try:
        credentials = LoginRequest(email=email, password=password)
    except ValidationError as exc:
        raise InvalidAdministratorCredentials from exc

    normalized_email = str(credentials.email).lower()
    _lock_user_table_for_bootstrap(db)

    if has_super_administrator(db):
        raise AdministratorAlreadyProvisioned

    email_exists = db.scalar(
        select(User.id)
        .where(func.lower(User.email) == normalized_email)
        .limit(1)
    )
    if email_exists is not None:
        raise AdministratorEmailUnavailable

    administrator = User(
        email=normalized_email,
        hashed_password=hash_password(credentials.password),
        role="super_admin",
        is_active=True,
    )
    db.add(administrator)
    db.flush()
    return administrator
