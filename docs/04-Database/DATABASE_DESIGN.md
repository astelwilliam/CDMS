# Database Design

**Status**: Draft

## 1. Purpose
This document defines the conceptual database design for Version 1 of the Campus Department Management System (CDMS). It translates the approved business domain into a technology-independent data model that supports data integrity, consistency, and future extensibility while remaining aligned with the approved business entities and rules.

## 2. Design Principles

### Data Integrity
Data must accurately reflect business reality. Relationships and constraints must prevent invalid states such as orphaned content or inconsistent ownership.

### Consistency
All data objects must follow consistent naming, structure, and lifecycle patterns across the system to support maintainability and reduce complexity.

### Maintainability
The design must support clear understanding of data objects and their relationships, enabling future modifications with minimal disruption.

### Scalability
The conceptual model must allow for growth in data volume and the addition of new entities without requiring fundamental redesign.

### Normalization
Data should be organized to reduce redundancy while maintaining performance and query simplicity appropriate for Version 1.

### Extensibility
The design must accommodate future versions by allowing new entities and relationships to be added with minimal impact on existing structures.

## 3. Data Objects

### College
**Purpose**: Represents the top-level educational institution.

**Description**: The College is the root organizational unit that contains departments and system-wide configurations.

**Suggested Business Attributes**: Name, description, contact information, logo reference.

**Required Attributes**: Name

**Optional Attributes**: Description, contact information, logo reference

**Validation Considerations**: Name must be unique within the system.

### Department
**Purpose**: Represents an academic unit within the college.

**Description**: A Department manages its own public content and is the primary context for most Version 1 entities.

**Suggested Business Attributes**: Name, description, contact information, website settings.

**Required Attributes**: Name, College association

**Optional Attributes**: Description, contact information

**Validation Considerations**: Name must be unique within a College.

### Faculty Member
**Purpose**: Represents an academic staff member.

**Description**: Faculty Members are associated with a single department and may be displayed publicly.

**Suggested Business Attributes**: Name, title, biography, contact information, profile image reference.

**Required Attributes**: Name, Department association

**Optional Attributes**: Title, biography, contact information, profile image reference

**Validation Considerations**: A Faculty Member must belong to exactly one Department.

### Announcement
**Purpose**: Represents time-sensitive published information.

**Description**: Announcements may be created at department or college level and follow a publication lifecycle.

**Suggested Business Attributes**: Title, content, publication date, expiration date.

**Required Attributes**: Title, content, owning Department or College

**Optional Attributes**: Publication date, expiration date

**Validation Considerations**: Must belong to either one Department or the College.

### Event
**Purpose**: Represents scheduled departmental activities.

**Description**: Events are owned by a department and may be associated with multiple images.

**Suggested Business Attributes**: Title, description, date and time, location.

**Required Attributes**: Title, owning Department

**Optional Attributes**: Description, date and time, location

**Validation Considerations**: An Event belongs to exactly one Department.

### Academic Resource
**Purpose**: Represents academic materials published by a department.

**Description**: Academic Resources are owned and maintained by a department.

**Suggested Business Attributes**: Title, description, file reference or link.

**Required Attributes**: Title, owning Department

**Optional Attributes**: Description, file reference or link

**Validation Considerations**: Belongs to exactly one Department.

### Timetable
**Purpose**: Represents class or academic activity schedules.

**Description**: Timetables are managed at the department level.

**Suggested Business Attributes**: Title, description, schedule period.

**Required Attributes**: Title, owning Department

**Optional Attributes**: Description, schedule period

**Validation Considerations**: Belongs to exactly one Department.

### Gallery Album
**Purpose**: Represents a collection of images.

**Description**: Gallery Albums organize visual content for a department.

**Suggested Business Attributes**: Title, description.

**Required Attributes**: Title, owning Department

**Optional Attributes**: Description

**Validation Considerations**: Belongs to exactly one Department.

### Gallery Image
**Purpose**: Represents an individual image.

**Description**: Gallery Images belong to one Gallery Album.

**Suggested Business Attributes**: Title, description, image reference.

**Required Attributes**: Gallery Album association

**Optional Attributes**: Title, description, image reference

**Validation Considerations**: Must belong to exactly one Gallery Album.

### Academic Calendar
**Purpose**: Represents academic dates and schedules.

**Description**: Academic Calendars are managed at the department level.

**Suggested Business Attributes**: Title, description, academic year or term.

**Required Attributes**: Title, owning Department

**Optional Attributes**: Description, academic year or term

**Validation Considerations**: Belongs to exactly one Department.

### Help Center Article
**Purpose**: Represents support and informational content.

**Description**: Help Center Articles are maintained by a department to assist users.

**Suggested Business Attributes**: Title, content, category.

**Required Attributes**: Title, content, owning Department

**Optional Attributes**: Category

**Validation Considerations**: Belongs to exactly one Department.

### Settings
**Purpose**: Represents configuration parameters.

**Description**: Settings exist at both college and department levels.

**Suggested Business Attributes**: Key, value, scope (college or department).

**Required Attributes**: Key, value, scope

**Optional Attributes**: None

**Validation Considerations**: Keys must be unique within their scope (college or department).

### Audit Log
**Purpose**: Records significant administrative actions.

**Description**: Audit Logs provide traceability of changes made by administrators.

**Suggested Business Attributes**: Action type, timestamp, performed by, affected object.

**Required Attributes**: Action type, timestamp, performed by

**Optional Attributes**: Affected object reference, additional details

**Validation Considerations**: Must record actions performed by administrators.

### Role
**Purpose**: Represents categories of access rights.

**Description**: Roles group permissions for administrative users.

**Suggested Business Attributes**: Name, description.

**Required Attributes**: Name

**Optional Attributes**: Description

**Validation Considerations**: Name must be unique.

### Permission
**Purpose**: Represents specific rights to perform actions.

**Description**: Permissions define granular actions available in the system.

**Suggested Business Attributes**: Name, description.

**Required Attributes**: Name

**Optional Attributes**: Description

**Validation Considerations**: Name must be unique.

### Department Administrator
**Purpose**: Represents users who manage departmental content.

**Description**: Department Administrators are assigned to one or more departments.

**Suggested Business Attributes**: Name, email, assigned departments.

**Required Attributes**: Name, email, Role assignment

**Optional Attributes**: Assigned departments

**Validation Considerations**: Must be assigned at least one Department.

### Super Administrator
**Purpose**: Represents system-level oversight users.

**Description**: Super Administrators have broad access across the college and all departments.

**Suggested Business Attributes**: Name, email, Role assignment.

**Required Attributes**: Name, email, Role assignment

**Optional Attributes**: None

**Validation Considerations**: Must hold a Super Administrator role.

## 4. Conceptual Relationships

The Department serves as the central organizing concept. Most data objects are associated with a specific Department.

- A College contains multiple Departments.
- A Department belongs to one College.
- Faculty Members, Events, Academic Resources, Timetables, Gallery Albums, Academic Calendars, and Help Center Articles belong to one Department.
- Announcements may belong to either a Department or the College.
- Gallery Images belong to one Gallery Album.
- Events may be associated with multiple Gallery Images.
- Settings exist independently at College level and Department level.
- Audit Logs record actions performed on multiple data objects.
- Roles and Permissions support access control for Department Administrators and Super Administrators.
- Department Administrators are associated with one or more Departments.

## 5. Business Constraints

- A Faculty Member must belong to exactly one Department.
- An Announcement must belong to either one Department or the College.
- All publishable content must pass through defined lifecycle states before becoming visible.
- Settings keys must be unique within their scope (College or Department).
- Important administrative actions must be recorded in Audit Logs.
- Department Administrators must be assigned to at least one Department.
- Gallery Images must belong to exactly one Gallery Album.

## 6. Lifecycle Data

Most publishable entities (Announcement, Event, Academic Resource, Timetable, Gallery Album, Help Center Article) follow a common lifecycle represented as states:

**Draft** → **Published** → **Archived**

- Draft: Content is being prepared and is not visible publicly.
- Published: Content is live and visible on the public website.
- Archived: Content is no longer active but remains stored for historical purposes.

Some entities (Faculty Member, Gallery Image) may use simpler states such as Active / Inactive.

## 7. Audit Requirements

The following data objects require audit history:

- Department
- Faculty Member
- Announcement
- Event
- Academic Resource
- Timetable
- Gallery Album
- Gallery Image
- Academic Calendar
- Help Center Article
- Settings
- Department Administrator

**Rationale**: These objects represent core business content and administrative actions. Recording changes supports accountability, recovery, and compliance requirements.

## 8. Soft Delete Policy

The following data objects support soft deletion:

- Department
- Faculty Member
- Announcement
- Event
- Academic Resource
- Timetable
- Gallery Album
- Gallery Image
- Academic Calendar
- Help Center Article

**Rationale**: Soft deletion preserves historical data, supports recovery from accidental deletion, and maintains referential integrity for audit and reporting purposes.

## 9. Open Questions

- How should college-wide Settings interact with department-level Settings when conflicts occur?
- Should Audit Logs capture changes to all entities or only a defined subset?
- What is the precise relationship between Academic Calendar and Events (are they independent or linked)?
- Should Help Center Articles support categories or tags as part of their core attributes?

---

**Document Version**: 1.0  
**Status**: Draft  
**Last Updated**: 2026-07-23  
**Depends On**: DOMAIN_MODEL.md (Approved), SOFTWARE_REQUIREMENTS_SPECIFICATION.md, ARCHITECTURE_DECISIONS.md  
**Referenced By**: Future database implementation documents