from app.models.college import College
from app.models.department import Department
from app.models.faculty_member import FacultyMember
from app.models.announcement import Announcement
from app.models.event import Event
from app.models.academic_resource import AcademicResource
from app.models.timetable import Timetable
from app.models.gallery_album import GalleryAlbum
from app.models.gallery_image import GalleryImage
from app.models.academic_calendar import AcademicCalendar
from app.models.help_center_article import HelpCenterArticle
from app.models.setting import Setting
from app.models.audit_log import AuditLog
from app.models.role import Role
from app.models.permission import Permission
from app.models.department_administrator import DepartmentAdministrator
from app.models.super_administrator import SuperAdministrator

from app.models.association_tables import (
    event_gallery_images,
    role_permissions,
    department_administrator_departments,
)
