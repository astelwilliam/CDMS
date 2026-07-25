# SQLAlchemy Models Specification

**Status**: Draft

## 1. Purpose
This document defines the SQLAlchemy ORM model architecture for Version 1 of the Campus Department Management System (CDMS). It specifies how the approved business entities and physical PostgreSQL schema will be represented in the ORM layer while maintaining alignment with the approved Domain Model, Database Design, Entity Relationship Diagram, Data Dictionary, and PostgreSQL Schema Specification.

## 2. ORM Design Principles

### Separation of Concerns
The ORM layer should focus exclusively on data persistence and object-relational mapping. Business logic must reside in the service layer, and presentation concerns must remain outside the model layer.

### Type Safety
All models should leverage SQLAlchemy’s type system to ensure type safety and reduce runtime errors during development and maintenance.

### Relationship Management
Relationships between entities must be clearly defined using SQLAlchemy relationship constructs while avoiding unnecessary complexity in the model layer.

### Lazy vs Eager Loading Strategy
The design should favor lazy loading by default for most relationships to optimize performance. Eager loading should be applied selectively through query options when specific use cases require it.

### Maintainability
Models should be organized in a way that supports long-term maintainability, with clear naming and structure that mirrors the approved business entities.

### Reusability
Common behaviors such as timestamp management and soft deletion should be implemented through reusable mixins rather than duplicated across models.

## 3. Base Model

All ORM models should inherit from a common base model that provides core functionality required across the system.

The base model should conceptually include:

- `id`: Primary key identifier (UUID)
- `created_at`: Timestamp of record creation
- `updated_at`: Timestamp of last modification
- `deleted_at`: Timestamp used for soft deletion (where applicable)

This base provides consistent structure and behavior for all persistent entities.

## 4. Entity Models

### College
**Model Name**: College  
**Database Table**: colleges  
**Purpose**: Represents the top-level educational institution.

**Attributes**: All columns defined in the PostgreSQL schema specification for the `colleges` table.

**Relationships**:
- One-to-Many with Department
- One-to-Many with Announcement (college-wide)
- One-to-Many with Settings (college scope)

**Cascade Behavior**: Appropriate cascading for related departments and settings.

**Soft Delete Support**: Not required.

### Department
**Model Name**: Department  
**Database Table**: departments  
**Purpose**: Represents academic departments.

**Attributes**: All columns defined in the PostgreSQL schema specification for the `departments` table.

**Relationships**:
- Many-to-One with College
- One-to-Many with Faculty Member, Announcement, Event, Academic Resource, Timetable, Gallery Album, Academic Calendar, Help Center Article, Settings

**Cascade Behavior**: Restrict on delete for most child entities.

**Soft Delete Support**: Yes.

### Faculty Member
**Model Name**: FacultyMember  
**Database Table**: faculty_members  
**Purpose**: Represents academic staff members.

**Attributes**: All columns defined in the PostgreSQL schema specification for the `faculty_members` table.

**Relationships**:
- Many-to-One with Department

**Cascade Behavior**: Restrict on delete.

**Soft Delete Support**: Yes.

### Announcement
**Model Name**: Announcement  
**Database Table**: announcements  
**Purpose**: Represents published announcements.

**Attributes**: All columns defined in the PostgreSQL schema specification for the `announcements` table.

**Relationships**:
- Many-to-One with Department (optional)
- Many-to-One with College (optional)

**Cascade Behavior**: Set null on delete of owning department or college.

**Soft Delete Support**: Yes.

### Event
**Model Name**: Event  
**Database Table**: events  
**Purpose**: Represents departmental events.

**Attributes**: All columns defined in the PostgreSQL schema specification for the `events` table.

**Relationships**:
- Many-to-One with Department
- Many-to-Many with Gallery Image

**Cascade Behavior**: Restrict on delete.

**Soft Delete Support**: Yes.

### Academic Resource
**Model Name**: AcademicResource  
**Database Table**: academic_resources  
**Purpose**: Represents academic materials.

**Attributes**: All columns defined in the PostgreSQL schema specification for the `academic_resources` table.

**Relationships**:
- Many-to-One with Department

**Cascade Behavior**: Restrict on delete.

**Soft Delete Support**: Yes.

### Timetable
**Model Name**: Timetable  
**Database Table**: timetables  
**Purpose**: Represents departmental schedules.

**Attributes**: All columns defined in the PostgreSQL schema specification for the `timetables` table.

**Relationships**:
- Many-to-One with Department

**Cascade Behavior**: Restrict on delete.

**Soft Delete Support**: Yes.

### Gallery Album
**Model Name**: GalleryAlbum  
**Database Table**: gallery_albums  
**Purpose**: Represents collections of images.

**Attributes**: All columns defined in the PostgreSQL schema specification for the `gallery_albums` table.

**Relationships**:
- Many-to-One with Department
- One-to-Many with Gallery Image

**Cascade Behavior**: Cascade delete to images.

**Soft Delete Support**: Yes.

### Gallery Image
**Model Name**: GalleryImage  
**Database Table**: gallery_images  
**Purpose**: Represents individual images.

**Attributes**: All columns defined in the PostgreSQL schema specification for the `gallery_images` table.

**Relationships**:
- Many-to-One with Gallery Album
- Many-to-Many with Event

**Cascade Behavior**: Cascade on album delete.

**Soft Delete Support**: Yes.

### Academic Calendar
**Model Name**: AcademicCalendar  
**Database Table**: academic_calendars  
**Purpose**: Represents academic date information.

**Attributes**: All columns defined in the PostgreSQL schema specification for the `academic_calendars` table.

**Relationships**:
- Many-to-One with Department

**Cascade Behavior**: Restrict on delete.

**Soft Delete Support**: Yes.

### Help Center Article
**Model Name**: HelpCenterArticle  
**Database Table**: help_center_articles  
**Purpose**: Represents support content.

**Attributes**: All columns defined in the PostgreSQL schema specification for the `help_center_articles` table.

**Relationships**:
- Many-to-One with Department

**Cascade Behavior**: Restrict on delete.

**Soft Delete Support**: Yes.

### Settings
**Model Name**: Setting  
**Database Table**: settings  
**Purpose**: Represents configuration values.

**Attributes**: All columns defined in the PostgreSQL schema specification for the `settings` table.

**Relationships**:
- Many-to-One with College (optional)
- Many-to-One with Department (optional)

**Cascade Behavior**: Cascade on delete.

**Soft Delete Support**: Not required.

### Audit Log
**Model Name**: AuditLog  
**Database Table**: audit_logs  
**Purpose**: Records administrative actions.

**Attributes**: All columns defined in the PostgreSQL schema specification for the `audit_logs` table.

**Relationships**:
- Many-to-One with Department Administrator or Super Administrator

**Cascade Behavior**: Restrict on delete.

**Soft Delete Support**: Not required.

### Role
**Model Name**: Role  
**Database Table**: roles  
**Purpose**: Defines access control roles.

**Attributes**: All columns defined in the PostgreSQL schema specification for the `roles` table.

**Relationships**:
- One-to-Many with Department Administrator and Super Administrator

**Cascade Behavior**: Restrict on delete.

**Soft Delete Support**: Not required.

### Permission
**Model Name**: Permission  
**Database Table**: permissions  
**Purpose**: Defines granular permissions.

**Attributes**: All columns defined in the PostgreSQL schema specification for the `permissions` table.

**Relationships**:
- Many-to-Many with Role

**Cascade Behavior**: Restrict on delete.

**Soft Delete Support**: Not required.

### Department Administrator
**Model Name**: DepartmentAdministrator  
**Database Table**: department_administrators  
**Purpose**: Represents department-level administrators.

**Attributes**: All columns defined in the PostgreSQL schema specification for the `department_administrators` table.

**Relationships**:
- Many-to-One with Role
- Many-to-Many with Department

**Cascade Behavior**: Restrict on delete.

**Soft Delete Support**: Not required.

### Super Administrator
**Model Name**: SuperAdministrator  
**Database Table**: super_administrators  
**Purpose**: Represents system-level administrators.

**Attributes**: All columns defined in the PostgreSQL schema specification for the `super_administrators` table.

**Relationships**:
- Many-to-One with Role

**Cascade Behavior**: Restrict on delete.

**Soft Delete Support**: Not required.

## 5. Relationship Strategy

- One-to-One relationships are used where a single record has a direct exclusive relationship with another (rare in Version 1).
- One-to-Many relationships represent the most common pattern (e.g., Department to Faculty Members).
- Many-to-Many relationships are implemented through association tables when needed (e.g., Event and Gallery Image, Role and Permission).
- Bidirectional relationships should be defined consistently on both sides of the association to maintain object graph integrity.

## 6. Validation Strategy

- Basic validation (required fields, uniqueness) should be enforced at the database level through constraints.
- ORM-level validation should be limited to type checking and relationship integrity.
- Complex business validation must be handled in the service layer rather than within the model layer.

## 7. Loading Strategy

Lazy loading is recommended as the default for most relationships to optimize memory usage and query performance. Eager loading should be applied explicitly through query options only when the use case requires immediate access to related objects.

## 8. Inheritance Strategy

No table inheritance is required for Version 1. All entities are represented as independent tables with their own attributes and relationships.

## 9. Common Mixins

### TimestampMixin
Provides `created_at` and `updated_at` columns for automatic timestamp management.

### SoftDeleteMixin
Provides `deleted_at` column and supporting logic for soft deletion where applicable.

### AuditMixin
Provides fields and behavior for tracking creation and modification by users (where required).

## 10. Best Practices

- Keep models focused on persistence concerns only.
- Use mixins for shared behavior instead of duplication.
- Define relationships clearly and consistently.
- Prefer lazy loading unless eager loading provides clear performance benefits.
- Maintain separation between the ORM layer and business logic.
- Follow naming conventions established in the PostgreSQL Schema Specification.

## 11. Open Questions

- Should bidirectional relationships be defined on both sides for all associations or only selected ones?
- Is there a need for a polymorphic association for Audit Log references to different administrator types?
- Should relationship loading strategies be defined at the model level or only at the query level?

---

**Document Version**: 1.0  
**Status**: Draft  
**Last Updated**: 2026-07-23  
**Depends On**: DOMAIN_MODEL.md, DATABASE_DESIGN.md, ENTITY_RELATIONSHIP_DIAGRAM.md, DATA_DICTIONARY.md, POSTGRESQL_SCHEMA_SPECIFICATION.md  
**Referenced By**: Future backend implementation documents