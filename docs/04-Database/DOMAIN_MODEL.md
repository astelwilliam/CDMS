# Domain Model

**Status**: Draft for Review

## 1. Purpose
This document defines the business domain of the Campus Department Management System (CDMS) at a conceptual level. It identifies the core business entities, their responsibilities, relationships, and governing rules without referencing any technical implementation, database structure, or API design. The domain model serves as a shared understanding between business stakeholders and the development team.

## 2. Domain Overview
The CDMS domain centers on managing and publishing academic departmental information for a college. The system supports three primary user perspectives:

- **Public visitors** who consume departmental information
- **Department Administrators** who manage content for their specific department
- **Super Administrators** who oversee the entire college and multiple departments

The domain focuses on structured content management for academic departments while maintaining clear ownership and publishing controls.

## 3. Core Business Entities

### 3.1 Organization

#### College
**Purpose**: Represents the top-level educational institution.

**Description**: A College contains one or more academic departments and is managed by Super Administrators.

**Primary Responsibilities**:
- Holds college-wide profile information
- Owns system-wide settings and announcements
- Provides context for all departments

**Owned By**: Super Administrator

#### Department
**Purpose**: Represents an academic unit within the college.

**Description**: A Department is the primary organizational unit responsible for managing its own content and resources.

**Primary Responsibilities**:
- Owns and manages its public website content
- Controls its faculty listings, announcements, events, and resources
- Defines its own academic calendar and timetables

**Owned By**: Super Administrator (primary), Department Administrator (operational)

### 3.2 Administration

#### Department Administrator
**Purpose**: Represents a user responsible for managing a specific department’s content.

**Description**: Department Administrators have permission to create, update, and publish content within their assigned department.

**Primary Responsibilities**:
- Manages departmental content and resources
- Controls the publishing status of department-owned entities

**Owned By**: Super Administrator

#### Super Administrator
**Purpose**: Represents a system-level user with oversight across all departments.

**Description**: Super Administrators manage college-level settings, departments, and department administrators.

**Primary Responsibilities**:
- Manages college profile and system-wide configurations
- Oversees department administrators and college-wide announcements

**Owned By**: Not applicable (top-level role)

#### Settings
**Purpose**: Represents configurable parameters at both college and department levels.

**Description**: Settings control behavior and appearance of the system for departments and the college as a whole.

**Primary Responsibilities**:
- Stores configuration values for departments and the college
- Influences how content and features are presented

**Owned By**: Super Administrator (college-level), Department Administrator (department-level)

#### Audit Log
**Purpose**: Represents a record of significant administrative actions performed in the system.

**Description**: Audit Logs provide traceability of changes made by administrators.

**Primary Responsibilities**:
- Records key administrative activities
- Supports accountability and historical review

**Owned By**: Super Administrator

### 3.3 Academic

#### Faculty Member
**Purpose**: Represents an academic staff member associated with a department.

**Description**: A Faculty Member is a person affiliated with a specific department who may be displayed on the public website.

**Primary Responsibilities**:
- Provides professional information for public display
- Belongs to exactly one department

**Owned By**: Department Administrator

#### Academic Calendar
**Purpose**: Represents the schedule of academic activities and important dates for a department.

**Description**: An Academic Calendar organizes term dates, holidays, examination periods, and other academic events.

**Primary Responsibilities**:
- Provides structured academic scheduling information to the public
- Is managed by the owning department

**Owned By**: Department Administrator

#### Timetable
**Purpose**: Represents the schedule of classes or academic activities for a department.

**Description**: A Timetable organizes academic sessions by time, day, and other relevant attributes.

**Primary Responsibilities**:
- Presents structured scheduling information to the public
- Is managed by the owning department

**Owned By**: Department Administrator

### 3.4 Content

#### Announcement
**Purpose**: Represents time-sensitive information published by a department or the college.

**Description**: Announcements are used to communicate important updates to students, faculty, and visitors.

**Primary Responsibilities**:
- Conveys official departmental or college-wide messages
- Has a defined publication period

**Owned By**: Department Administrator (department), Super Administrator (college-wide)

#### Event
**Purpose**: Represents scheduled activities organized by a department.

**Description**: Events include seminars, workshops, conferences, and other departmental activities.

**Primary Responsibilities**:
- Provides event details for public viewing
- May be associated with multiple images

**Owned By**: Department Administrator

#### Academic Resource
**Purpose**: Represents downloadable or viewable academic materials.

**Description**: Academic Resources include documents, presentations, syllabi, and other learning materials published by a department.

**Primary Responsibilities**:
- Provides access to educational content
- Is owned and maintained by a department

**Owned By**: Department Administrator

#### Gallery Album
**Purpose**: Represents a collection of images related to a department.

**Description**: Gallery Albums organize visual content such as campus events, facilities, or departmental activities.

**Primary Responsibilities**:
- Groups related images together
- Provides structured visual storytelling

**Owned By**: Department Administrator

#### Gallery Image
**Purpose**: Represents an individual image within a gallery.

**Description**: A Gallery Image is a visual asset associated with a Gallery Album.

**Primary Responsibilities**:
- Stores visual content for public display
- Belongs to one Gallery Album

**Owned By**: Department Administrator

### 3.5 Support

#### Help Center Article
**Purpose**: Represents informational content provided to help users navigate the departmental website.

**Description**: Help Center Articles contain guidance, FAQs, and support information for visitors and administrators.

**Primary Responsibilities**:
- Provides assistance and explanatory content to users
- Is maintained to support user experience

**Owned By**: Department Administrator

### 3.6 System

#### Role
**Purpose**: Represents a category of access rights assigned to users.

**Description**: Roles define groups of permissions that determine what actions a user can perform.

**Primary Responsibilities**:
- Groups permissions for administrative users
- Supports role-based access control

**Owned By**: Super Administrator

#### Permission
**Purpose**: Represents a specific right to perform an action within the system.

**Description**: Permissions define granular actions that can be granted to roles.

**Primary Responsibilities**:
- Defines allowable actions in the system
- Supports fine-grained access control

**Owned By**: Super Administrator

## 4. Entity Relationships

The **Department** serves as the central business concept in Version 1. Most entities are owned and managed within the context of a specific department.

Key business relationships include:

- A **College** contains one or more **Departments**.
- A **Department** belongs to one **College**.
- A **Department** owns and manages the majority of its content entities, including Faculty Members, Announcements, Events, Academic Resources, Timetables, Gallery Albums, Gallery Images, and Academic Calendar.
- An **Announcement** may belong to either a **Department** or the **College** (for college-wide announcements).
- A **Faculty Member** belongs to exactly one **Department**.
- An **Event** belongs to one **Department** and may be associated with multiple **Gallery Images**.
- A **Gallery Album** belongs to one **Department** and contains zero or more **Gallery Images**.
- A **Department Administrator** is responsible for one **Department**.
- A **Super Administrator** oversees the **College** and all **Departments**, including the management of Department Administrators.
- **Settings** exist at both the **College** and **Department** levels.
- **Audit Logs** record actions performed by both **Department Administrators** and **Super Administrators**.
- **Role** and **Permission** entities support the assignment of access rights to administrators across the system.

## 5. Business Rules

- A Faculty Member belongs to exactly one Department.
- An Announcement belongs to either one Department or the College.
- An Event belongs to one Department.
- A Gallery Album contains zero or more Gallery Images.
- An Event may be associated with multiple Gallery Images.
- Only Department Administrators may manage content for their assigned department.
- Only Super Administrators may manage college profile, departments, and department administrators.
- Content must go through defined lifecycle states before becoming publicly visible.
- Important business entities support soft deletion to preserve historical data.
- Academic Calendar and Timetable information is managed at the department level.
- Help Center Articles are maintained by the department to support its public website users.
- Settings may exist at both the college level and the department level.
- Administrative actions that modify important business entities are recorded in Audit Logs.

## 6. Entity Lifecycle

Most publishable entities follow a similar lifecycle:

**Draft** → **Published** → **Archived**

- **Draft**: Content is being prepared and is not visible to the public.
- **Published**: Content is live and visible on the public website.
- **Archived**: Content is no longer active but remains accessible for historical purposes.

Some entities (such as Faculty Members and Gallery Images) may follow simpler states (Active / Inactive).

## 7. Ownership

| Entity                | Primary Owner                  | Secondary Oversight     |
|-----------------------|--------------------------------|-------------------------|
| College               | Super Administrator            | -                       |
| Department            | Super Administrator            | Department Administrator |
| Faculty Member        | Department Administrator       | Super Administrator     |
| Announcement          | Department Administrator       | Super Administrator     |
| Event                 | Department Administrator       | Super Administrator     |
| Academic Resource     | Department Administrator       | Super Administrator     |
| Timetable             | Department Administrator       | Super Administrator     |
| Gallery Album         | Department Administrator       | Super Administrator     |
| Gallery Image         | Department Administrator       | Super Administrator     |
| Academic Calendar     | Department Administrator       | Super Administrator     |
| Help Center Article   | Department Administrator       | Super Administrator     |
| Settings              | Super Administrator (college), Department Administrator (department) | - |
| Audit Log             | Super Administrator            | -                       |
| Role                  | Super Administrator            | -                       |
| Permission            | Super Administrator            | -                       |
| Department Administrator | Super Administrator         | -                       |

## 8. Future Expansion

Version 2 and beyond may introduce additional domain concepts such as:
- Student
- Course
- Assignment
- Attendance Record
- Examination
- Notification

These entities are explicitly excluded from the Version 1 domain model.

## 9. Open Questions

- **Open Question**: What is the precise scope and ownership model for the Help Center content?
- **Open Question**: Are Reports considered business entities, or are they dynamically generated views?
- **Open Question**: Should Academic Resources support versioning or only single published versions?

---

**Document Version**: 1.0  
**Status**: Approved  
**Last Updated**: 2026-07-23  
**Depends On**: SOFTWARE_REQUIREMENTS_SPECIFICATION.md, SYSTEM_ARCHITECTURE.md, ARCHITECTURE_DECISIONS.md  
**Referenced By**: DATABASE_DESIGN.md (future), MODULE_SPECIFICATIONS.md (future)