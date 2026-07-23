from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import declared_attr
from app.db.session import Base


class TimestampMixin:
    """Mixin that adds created_at and updated_at timestamps."""

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


class SoftDeleteMixin:
    """Mixin that adds soft delete support via deleted_at column."""

    deleted_at = Column(DateTime(timezone=True), nullable=True)
