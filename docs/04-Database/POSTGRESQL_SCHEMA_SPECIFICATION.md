# PostgreSQL Schema Specification

**Status**: Draft

## 1. Purpose
This document defines the physical PostgreSQL database schema for Version 1 of the Campus Department Management System (CDMS). It specifies how the approved business entities, relationships, and rules from the Domain Model, Database Design, Entity Relationship Diagram, and Data Dictionary will be represented in PostgreSQL while maintaining alignment with the approved business requirements.

## 2. Naming Standards

### Table Names
- Use plural form in `snake_case` (e.g., `departments`, `faculty_members`).
- Names should be descriptive and reflect the business entity.

### Column Names
- Use `snake_case`.
- Primary keys should be named `id`.
- Foreign keys should follow the pattern `referenced_table_id` (e.g., `department_id`).

### Primary Keys
- All tables use `id` as the primary key column.
- Primary keys are implemented as UUID.

### Foreign Keys
- Foreign key columns follow the naming pattern `referenced_table_id`.
- Foreign key constraint names follow the pattern `fk_<source_table>_<target_table>`.

### Index Names
- Indexes follow the pattern `idx_<table>_<column(s)>`.

### Constraint Names
- Primary key constraints: `pk_<table_name>`
- Unique constraints: `uq_<table>_<column>`
- Check constraints: `ck_<table>_<description>`

## 3. Tables

### colleges
**Purpose**: Stores information about the college.

**Primary Key**: `id` (UUID)

| Column                    | PostgreSQL Data Type | Nullable | Default Value | Description |
|---------------------------|----------------------|----------|---------------|-------------|
| id                        | uuid                 | No       | -             | Unique identifier |
| name                      | text                 | No       | -             | Official name of the college |
| description               | text                 | Yes      | -             | Brief overview of the college |
| contact_information       | text                 | Yes      | -             | Contact details |
| logo_reference            | text                 | Yes      | -             | Reference to logo |
| created_at                | timestamp with time zone | No   | -             | Record creation timestamp |
| updated_at                | timestamp with time zone | No   | -             | Last update timestamp |

### departments
**Purpose**: Stores academic departments within the college.

**Primary Key**: `id` (UUID)

| Column                    | PostgreSQL Data Type | Nullable | Default Value | Description |
|---------------------------|----------------------|----------|---------------|-------------|
| id                        | uuid                 | No       | -             | Unique identifier |
| college_id                | uuid                 | No       | -             | Reference to parent college |
| name                      | text                 | No       | -             | Name of the department |
| description               | text                 | Yes      | -             | Description of the department |
| contact_information       | text                 | Yes      | -             | Contact details |
| created_at                | timestamp with time zone | No   | -             | Record creation timestamp |
| updated_at                | timestamp with time zone | No   | -             | Last update timestamp |
| deleted_at                | timestamp with time zone | Yes  | -             | Soft delete timestamp |

### faculty_members
**Purpose**: Stores faculty members associated with departments.

**Primary Key**: `id` (UUID)

| Column                    | PostgreSQL Data Type | Nullable | Default Value | Description |
|---------------------------|----------------------|----------|---------------|-------------|
| id                        | uuid                 | No       | -             | Unique identifier |
| department_id             | uuid                 | No       | -             | Reference to department |
| name                      | text                 | No       | -             | Full name |
| title                     | text                 | Yes      | -             | Academic title |
| biography                 | text                 | Yes      | -             | Professional biography |
| contact_information       | text                 | Yes      | -             | Contact details |
| profile_image_reference   | text                 | Yes      | -             | Profile image reference |
| created_at                | timestamp with time zone | No   | -             | Record creation timestamp |
| updated_at                | timestamp with time zone | No   | -             | Last update timestamp |
| deleted_at                | timestamp with time zone | Yes  | -             | Soft delete timestamp |

### announcements
**Purpose**: Stores announcements published by departments or the college.

**Primary Key**: `id` (UUID)

| Column                    | PostgreSQL Data Type | Nullable | Default Value | Description |
|---------------------------|----------------------|----------|---------------|-------------|
| id                        | uuid                 | No       | -             | Unique identifier |
| department_id             | uuid                 | Yes      | -             | Reference to department (nullable for college-wide) |
| college_id                | uuid                 | Yes      | -             | Reference to college (for college-wide announcements) |
| title                     | text                 | No       | -             | Title of the announcement |
| content                   | text                 | No       | -             | Main content |
| publication_date          | timestamp with time zone | Yes  | -             | When it becomes visible |
| expiration_date           | timestamp with time zone | Yes  | -             | When it expires |
| lifecycle_status          | text                 | No       | -             | Current lifecycle state |
| created_at                | timestamp with time zone | No   | -             | Record creation timestamp |
| updated_at                | timestamp with time zone | No   | -             | Last update timestamp |
| deleted_at                | timestamp with time zone | Yes  | -             | Soft delete timestamp |

### events
**Purpose**: Stores events organized by departments.

**Primary Key**: `id` (UUID)

| Column                    | PostgreSQL Data Type | Nullable | Default Value | Description |
|---------------------------|----------------------|----------|---------------|-------------|
| id                        | uuid                 | No       | -             | Unique identifier |
| department_id             | uuid                 | No       | -             | Reference to department |
| title                     | text                 | No       | -             | Title of the event |
| description               | text                 | Yes      | -             | Event description |
| date_and_time             | timestamp with time zone | Yes  | -             | Scheduled date and time |
| location                  | text                 | Yes      | -             | Event location |
| lifecycle_status          | text                 | No       | -             | Current lifecycle state |
| created_at                | timestamp with time zone | No   | -             | Record creation timestamp |
| updated_at                | timestamp with time zone | No   | -             | Last update timestamp |
| deleted_at                | timestamp with time zone | Yes  | -             | Soft delete timestamp |

### academic_resources
**Purpose**: Stores academic materials published by departments.

**Primary Key**: `id` (UUID)

| Column                    | PostgreSQL Data Type | Nullable | Default Value | Description |
|---------------------------|----------------------|----------|---------------|-------------|
| id                        | uuid                 | No       | -             | Unique identifier |
| department_id             | uuid                 | No       | -             | Reference to department |
| title                     | text                 | No       | -             | Title of the resource |
| description               | text                 | Yes      | -             | Description |
| file_reference_or_link    | text                 | Yes      | -             | File or link reference |
| lifecycle_status          | text                 | No       | -             | Current lifecycle state |
| created_at                | timestamp with time zone | No   | -             | Record creation timestamp |
| updated_at                | timestamp with time zone | No   | -             | Last update timestamp |
| deleted_at                | timestamp with time zone | Yes  | -             | Soft delete timestamp |

### timetables
**Purpose**: Stores departmental timetables.

**Primary Key**: `id` (UUID)

| Column                    | PostgreSQL Data Type | Nullable | Default Value | Description |
|---------------------------|----------------------|----------|---------------|-------------|
| id                        | uuid                 | No       | -             | Unique identifier |
| department_id             | uuid                 | No       | -             | Reference to department |
| title                     | text                 | No       | -             | Title of the timetable |
| description               | text                 | Yes      | -             | Description |
| schedule_period           | text                 | Yes      | -             | Time period covered |
| lifecycle_status          | text                 | No       | -             | Current lifecycle state |
| created_at                | timestamp with time zone | No   | -             | Record creation timestamp |
| updated_at                | timestamp with time zone | No   | -             | Last update timestamp |
| deleted_at                | timestamp with time zone | Yes  | -             | Soft delete timestamp |

### gallery_albums
**Purpose**: Stores collections of images for departments.

**Primary Key**: `id` (UUID)

| Column                    | PostgreSQL Data Type | Nullable | Default Value | Description |
|---------------------------|----------------------|----------|---------------|-------------|
| id                        | uuid                 | No       | -             | Unique identifier |
| department_id             | uuid                 | No       | -             | Reference to department |
| title                     | text                 | No       | -             | Title of the album |
| description               | text                 | Yes      | -             | Description |
| lifecycle_status          | text                 | No       | -             | Current lifecycle state |
| created_at                | timestamp with time zone | No   | -             | Record creation timestamp |
| updated_at                | timestamp with time zone | No   | -             | Last update timestamp |
| deleted_at                | timestamp with time zone | Yes  | -             | Soft delete timestamp |

### gallery_images
**Purpose**: Stores individual images within gallery albums.

**Primary Key**: `id` (UUID)

| Column                    | PostgreSQL Data Type | Nullable | Default Value | Description |
|---------------------------|----------------------|----------|---------------|-------------|
| id                        | uuid                 | No       | -             | Unique identifier |
| gallery_album_id          | uuid                 | No       | -             | Reference to album |
| title                     | text                 | Yes      | -             | Title or caption |
| description               | text                 | Yes      | -             | Description |
| image_reference           | text                 | No       | -             | Image file reference |
| created_at                | timestamp with time zone | No   | -             | Record creation timestamp |
| updated_at                | timestamp with time zone | No   | -             | Last update timestamp |
| deleted_at                | timestamp with time zone | Yes  | -             | Soft delete timestamp |

### academic_calendars
**Purpose**: Stores academic calendars for departments.

**Primary Key**: `id` (UUID)

| Column                    | PostgreSQL Data Type | Nullable | Default Value | Description |
|---------------------------|----------------------|----------|---------------|-------------|
| id                        | uuid                 | No       | -             | Unique identifier |
| department_id             | uuid                 | No       | -             | Reference to department |
| title                     | text                 | No       | -             | Title of the calendar |
| description               | text                 | Yes      | -             | Description |
| academic_year_or_term     | text                 | Yes      | -             | Year or term covered |
| lifecycle_status          | text                 | No       | -             | Current lifecycle state |
| created_at                | timestamp with time zone | No   | -             | Record creation timestamp |
| updated_at                | timestamp with time zone | No   | -             | Last update timestamp |
| deleted_at                | timestamp with time zone | Yes  | -             | Soft delete timestamp |

### help_center_articles
**Purpose**: Stores help and support articles for departments.

**Primary Key**: `id` (UUID)

| Column                    | PostgreSQL Data Type | Nullable | Default Value | Description |
|---------------------------|----------------------|----------|---------------|-------------|
| id                        | uuid                 | No       | -             | Unique identifier |
| department_id             | uuid                 | No       | -             | Reference to department |
| title                     | text                 | No       | -             | Title of the article |
| content                   | text                 | No       | -             | Article content |
| category                  | text                 | Yes      | -             | Category of the article |
| lifecycle_status          | text                 | No       | -             | Current lifecycle state |
| created_at                | timestamp with time zone | No   | -             | Record creation timestamp |
| updated_at                | timestamp with time zone | No   | -             | Last update timestamp |
| deleted_at                | timestamp with time zone | Yes  | -             | Soft delete timestamp |

### settings
**Purpose**: Stores configuration settings at college and department levels.

**Primary Key**: `id` (UUID)

| Column                    | PostgreSQL Data Type | Nullable | Default Value | Description |
|---------------------------|----------------------|----------|---------------|-------------|
| id                        | uuid                 | No       | -             | Unique identifier |
| college_id                | uuid                 | Yes      | -             | Reference to college (for college-level settings) |
| department_id             | uuid                 | Yes      | -             | Reference to department (for department-level settings) |
| key                       | text                 | No       | -             | Setting key |
| value                     | text                 | No       | -             | Setting value |
| scope                     | text                 | No       | -             | Scope (college or department) |
| created_at                | timestamp with time zone | No   | -             | Record creation timestamp |
| updated_at                | timestamp with time zone | No   | -             | Last update timestamp |

### audit_logs
**Purpose**: Records administrative actions for traceability.

**Primary Key**: `id` (UUID)

| Column                    | PostgreSQL Data Type | Nullable | Default Value | Description |
|---------------------------|----------------------|----------|---------------|-------------|
| id                        | uuid                 | No       | -             | Unique identifier |
| action_type               | text                 | No       | -             | Type of action performed |
| timestamp                 | timestamp with time zone | No   | -             | When the action occurred |
| performed_by_id           | uuid                 | No       | -             | Reference to the administrator |
| affected_object_reference | text                 | Yes      | -             | Reference to affected object |
| additional_details        | text                 | Yes      | -             | Additional information |
| created_at                | timestamp with time zone | No   | -             | Record creation timestamp |

### roles
**Purpose**: Defines roles for access control.

**Primary Key**: `id` (UUID)

| Column                    | PostgreSQL Data Type | Nullable | Default Value | Description |
|---------------------------|----------------------|----------|---------------|-------------|
| id                        | uuid                 | No       | -             | Unique identifier |
| name                      | text                 | No       | -             | Role name |
| description               | text                 | Yes      | -             | Role description |
| created_at                | timestamp with time zone | No   | -             | Record creation timestamp |
| updated_at                | timestamp with time zone | No   | -             | Last update timestamp |

### permissions
**Purpose**: Defines granular permissions.

**Primary Key**: `id` (UUID)

| Column                    | PostgreSQL Data Type | Nullable | Default Value | Description |
|---------------------------|----------------------|----------|---------------|-------------|
| id                        | uuid                 | No       | -             | Unique identifier |
| name                      | text                 | No       | -             | Permission name |
| description               | text                 | Yes      | -             | Permission description |
| created_at                | timestamp with time zone | No   | -             | Record creation timestamp |
| updated_at                | timestamp with time zone | No   | -             | Last update timestamp |

### department_administrators
**Purpose**: Stores department-level administrators.

**Primary Key**: `id` (UUID)

| Column                    | PostgreSQL Data Type | Nullable | Default Value | Description |
|---------------------------|----------------------|----------|---------------|-------------|
| id                        | uuid                 | No       | -             | Unique identifier |
| name                      | text                 | No       | -             | Full name |
| email                     | text                 | No       | -             | Email address |
| role_id                   | uuid                 | No       | -             | Reference to role |
| created_at                | timestamp with time zone | No   | -             | Record creation timestamp |
| updated_at                | timestamp with time zone | No   | -             | Last update timestamp |

### super_administrators
**Purpose**: Stores system-level administrators.

**Primary Key**: `id` (UUID)

| Column                    | PostgreSQL Data Type | Nullable | Default Value | Description |
|---------------------------|----------------------|----------|---------------|-------------|
| id                        | uuid                 | No       | -             | Unique identifier |
| name                      | text                 | No       | -             | Full name |
| email                     | text                 | No       | -             | Email address |
| role_id                   | uuid                 | No       | -             | Reference to role |
| created_at                | timestamp with time zone | No   | -             | Record creation timestamp |
| updated_at                | timestamp with time zone | No   | -             | Last update timestamp |

## 4. Relationships

- `departments.college_id` → `colleges.id` (Many-to-One, RESTRICT on delete)
- `faculty_members.department_id` → `departments.id` (Many-to-One, RESTRICT on delete)
- `announcements.department_id` → `departments.id` (Many-to-One, SET NULL on delete)
- `announcements.college_id` → `colleges.id` (Many-to-One, SET NULL on delete)
- `events.department_id` → `departments.id` (Many-to-One, RESTRICT on delete)
- `academic_resources.department_id` → `departments.id` (Many-to-One, RESTRICT on delete)
- `timetables.department_id` → `departments.id` (Many-to-One, RESTRICT on delete)
- `gallery_albums.department_id` → `departments.id` (Many-to-One, RESTRICT on delete)
- `gallery_images.gallery_album_id` → `gallery_albums.id` (Many-to-One, CASCADE on delete)
- `academic_calendars.department_id` → `departments.id` (Many-to-One, RESTRICT on delete)
- `help_center_articles.department_id` → `departments.id` (Many-to-One, RESTRICT on delete)
- `settings.college_id` → `colleges.id` (Many-to-One, CASCADE on delete)
- `settings.department_id` → `departments.id` (Many-to-One, CASCADE on delete)
- `department_administrators.role_id` → `roles.id` (Many-to-One, RESTRICT on delete)
- `super_administrators.role_id` → `roles.id` (Many-to-One, RESTRICT on delete)
- `audit_logs.performed_by_id` → `department_administrators.id` or `super_administrators.id` (Many-to-One, RESTRICT on delete)

## 5. Constraints

- Primary keys on all tables using `id` (UUID)
- Unique constraints on `name` for `colleges`, `departments`, `roles`, `permissions`
- Unique constraint on `email` for administrators
- Unique constraint on `key` + `scope` combination for `settings`
- Foreign key constraints as defined in Relationships section
- Check constraint ensuring `announcements` belongs to either `department_id` or `college_id`
- Check constraint on `settings.scope` to accept only 'college' or 'department'

## 6. Index Strategy

Recommended indexes include:

- Foreign key columns (`department_id`, `college_id`, `gallery_album_id`, `role_id`, etc.)
- Frequently searched fields (`name`, `title`, `email`)
- Lifecycle status columns for publishable entities
- Composite indexes on commonly queried combinations (e.g., `department_id` + `lifecycle_status`)

## 7. Audit Columns

The following audit columns are used across most tables:

- `created_at` (timestamp with time zone, NOT NULL)
- `updated_at` (timestamp with time zone, NOT NULL)
- `deleted_at` (timestamp with time zone, nullable) — for soft delete support

## 8. Soft Delete Strategy

Soft deletion is implemented using the `deleted_at` column on the following tables:

- departments
- faculty_members
- announcements
- events
- academic_resources
- timetables
- gallery_albums
- gallery_images
- academic_calendars
- help_center_articles

When `deleted_at` is not null, the record is considered deleted but remains in the database for historical and audit purposes.

## 9. Schema Validation Checklist

- [ ] All Version 1 entities from DOMAIN_MODEL.md are represented as tables
- [ ] Primary keys use UUID as per ARCHITECTURE_DECISIONS.md
- [ ] Foreign key relationships match the conceptual ERD
- [ ] Soft delete is applied to entities requiring it
- [ ] Audit columns are present on appropriate tables
- [ ] Lifecycle status column exists on publishable entities
- [ ] Unique constraints match business rules in DATA_DICTIONARY.md
- [ ] Naming follows the standards defined in this document

## 10. Open Questions

- Should `audit_logs` have a polymorphic relationship or separate columns for different administrator types?
- Is there a need for a junction table between `events` and `gallery_images` for the many-to-many relationship?
- Should `settings` support typed values (text, boolean, integer) instead of storing everything as text?

---

**Document Version**: 1.0  
**Status**: Draft  
**Last Updated**: 2026-07-23  
**Depends On**: DOMAIN_MODEL.md, DATABASE_DESIGN.md, ENTITY_RELATIONSHIP_DIAGRAM.md, DATA_DICTIONARY.md, ARCHITECTURE_DECISIONS.md  
**Referenced By**: Future implementation and migration documents