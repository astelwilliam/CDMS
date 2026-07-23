from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.base import TimestampMixin


class Role(Base, TimestampMixin):
    __tablename__ = "roles"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)

    # Relationships
    department_administrators = relationship("DepartmentAdministrator", back_populates="role")
    super_administrators = relationship("SuperAdministrator", back_populates="role")
    permissions = relationship(
        "Permission",
        secondary="role_permissions",
        back_populates="roles"
    )
