from collections.abc import Collection
from typing import List, Mapping
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from app.models.department import Department
from app.models.faculty_member import FacultyMember
from app.repositories.base import BaseRepository


class FacultyMemberRepository(BaseRepository[FacultyMember]):
    """Repository for FacultyMember entity."""

    _SCOPED_CREATE_FIELDS = frozenset(
        {
            "name",
            "title",
            "biography",
            "contact_information",
            "profile_image_reference",
        }
    )
    _SCOPED_UPDATE_FIELDS = _SCOPED_CREATE_FIELDS

    def __init__(self, db: Session):
        super().__init__(FacultyMember, db)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[FacultyMember]:
        stmt = select(FacultyMember).order_by(FacultyMember.id).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def get_by_department(self, department_id: str, skip: int = 0, limit: int = 100) -> List[FacultyMember]:
        """Get all active faculty members in a department."""
        stmt = (
            select(FacultyMember)
            .where(FacultyMember.department_id == department_id, FacultyMember.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_assigned(
        self,
        department_ids: Collection[str],
        skip: int = 0,
        limit: int = 100,
    ) -> list[FacultyMember]:
        stmt = (
            select(FacultyMember)
            .join(Department, Department.id == FacultyMember.department_id)
            .where(
                FacultyMember.department_id.in_(department_ids),
                FacultyMember.deleted_at.is_(None),
                Department.deleted_at.is_(None),
            )
            .order_by(FacultyMember.id)
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_assigned_by_id(
        self,
        faculty_member_id: str,
        department_ids: Collection[str],
    ) -> FacultyMember | None:
        return self.db.scalar(
            select(FacultyMember)
            .join(Department, Department.id == FacultyMember.department_id)
            .where(
                FacultyMember.id == faculty_member_id,
                FacultyMember.department_id.in_(department_ids),
                FacultyMember.deleted_at.is_(None),
                Department.deleted_at.is_(None),
            )
        )

    def get_for_scoped_write(
        self,
        faculty_member_id: str,
        department_id: str,
    ) -> FacultyMember | None:
        """Lock an active faculty row after earlier authorization locks are held."""
        return self.db.scalar(
            select(FacultyMember)
            .where(
                FacultyMember.id == faculty_member_id,
                FacultyMember.department_id == department_id,
                FacultyMember.deleted_at.is_(None),
            )
            .with_for_update()
        )

    def add_for_scoped_write(
        self,
        department_id: str,
        values: Mapping[str, object],
    ) -> FacultyMember:
        """Stage a faculty insert without committing the caller's transaction."""
        self._validate_scoped_fields(values, self._SCOPED_CREATE_FIELDS)
        faculty = FacultyMember(department_id=department_id, **values)
        self.db.add(faculty)
        self.db.flush()
        return faculty

    def update_for_scoped_write(
        self,
        faculty: FacultyMember,
        values: Mapping[str, object],
    ) -> FacultyMember:
        """Stage content updates without changing ownership or committing."""
        self._validate_scoped_fields(values, self._SCOPED_UPDATE_FIELDS)
        for field, value in values.items():
            setattr(faculty, field, value)
        self.db.flush()
        return faculty

    def soft_delete_for_scoped_write(
        self,
        faculty: FacultyMember,
    ) -> FacultyMember:
        """Stage a database-timestamped soft delete without committing."""
        if faculty.deleted_at is not None:
            raise ValueError("Faculty member is already deleted")
        faculty.deleted_at = self.db.scalar(select(func.now()))
        self.db.flush()
        return faculty

    @staticmethod
    def _validate_scoped_fields(
        values: Mapping[str, object],
        allowed_fields: frozenset[str],
    ) -> None:
        rejected_fields = set(values) - allowed_fields
        if rejected_fields:
            rejected = ", ".join(sorted(rejected_fields))
            raise ValueError(f"Unsupported scoped faculty fields: {rejected}")
