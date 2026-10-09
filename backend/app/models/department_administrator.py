import uuid
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.base import TimestampMixin


class DepartmentAdministrator(Base, TimestampMixin):
    __tablename__ = "department_administrators"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    role_id = Column(String(36), ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False, index=True)

    # Relationships
    role = relationship("Role", back_populates="department_administrators")
    departments = relationship(
        "Department",
        secondary="department_administrator_departments",
        back_populates="administrators"
    )
