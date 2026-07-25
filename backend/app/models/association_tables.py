from sqlalchemy import Column, String, ForeignKey, Table
from app.db.session import Base

# Many-to-Many: Event ↔ GalleryImage
event_gallery_images = Table(
    "event_gallery_images",
    Base.metadata,
    Column("event_id", String(36), ForeignKey("events.id", ondelete="CASCADE"), primary_key=True),
    Column("gallery_image_id", String(36), ForeignKey("gallery_images.id", ondelete="CASCADE"), primary_key=True),
)

# Many-to-Many: Role ↔ Permission
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", String(36), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", String(36), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)

# Many-to-Many: DepartmentAdministrator ↔ Department
department_administrator_departments = Table(
    "department_administrator_departments",
    Base.metadata,
    Column("department_administrator_id", String(36), ForeignKey("department_administrators.id", ondelete="CASCADE"), primary_key=True),
    Column("department_id", String(36), ForeignKey("departments.id", ondelete="CASCADE"), primary_key=True),
)
