# Data Dictionary

**Status**: Draft

## 1. Purpose
This document defines the business attributes for every approved Version 1 data object in the Campus Department Management System (CDMS). It provides a clear, technology-independent description of the data elements that support the approved business domain.

## 2. Scope
This Data Dictionary covers all approved Version 1 data objects as defined in the approved DOMAIN_MODEL.md, DATABASE_DESIGN.md, and ENTITY_RELATIONSHIP_DIAGRAM.md.

## 3. Data Dictionary

### College
| Attribute          | Description                                      | Required | Business Validation                     | Example                  |
|--------------------|--------------------------------------------------|----------|-----------------------------------------|--------------------------|
| Name               | Official name of the college                     | Yes      | Must be unique across the system        | "ABC Institute of Technology" |
| Description        | Brief overview of the college                    | No       | -                                       | "A leading technical institution" |
| Contact Information| Contact details for the college                  | No       | -                                       | "info@abc.edu"           |
| Logo Reference     | Reference to the college logo                    | No       | -                                       | -                        |

### Department
| Attribute          | Description                                      | Required | Business Validation                     | Example                  |
|--------------------|--------------------------------------------------|----------|-----------------------------------------|--------------------------|
| Name               | Name of the academic department                  | Yes      | Must be unique within the college       | "Computer Science"       |
| Description        | Description of the department                    | No       | -                                       | "Department of Computing"|
| Contact Information| Department contact details                       | No       | -                                       | "cs@abc.edu"             |

### Faculty Member
| Attribute          | Description                                      | Required | Business Validation                     | Example                  |
|--------------------|--------------------------------------------------|----------|-----------------------------------------|--------------------------|
| Name               | Full name of the faculty member                  | Yes      | -                                       | "Dr. Jane Smith"         |
| Title              | Academic or professional title                   | No       | -                                       | "Professor"              |
| Biography          | Professional biography                           | No       | -                                       | "Expert in AI and ML"    |
| Contact Information| Contact details                                  | No       | -                                       | "jane.smith@abc.edu"     |
| Profile Image Reference | Reference to profile image                  | No       | -                                       | -                        |

### Announcement
| Attribute          | Description                                      | Required | Business Validation                     | Example                  |
|--------------------|--------------------------------------------------|----------|-----------------------------------------|--------------------------|
| Title              | Title of the announcement                        | Yes      | -                                       | "Semester Registration Open" |
| Content            | Main body of the announcement                    | Yes      | -                                       | "Registration begins..." |
| Publication Date   | Date when the announcement becomes visible       | No       | -                                       | -                        |
| Expiration Date    | Date when the announcement is no longer active   | No       | -                                       | -                        |

### Event
| Attribute          | Description                                      | Required | Business Validation                     | Example                  |
|--------------------|--------------------------------------------------|----------|-----------------------------------------|--------------------------|
| Title              | Title of the event                               | Yes      | -                                       | "AI Workshop 2026"       |
| Description        | Description of the event                         | No       | -                                       | "Hands-on session on..." |
| Date and Time      | Scheduled date and time of the event             | No       | -                                       | -                        |
| Location           | Venue or location of the event                   | No       | -                                       | "Main Auditorium"        |

### Academic Resource
| Attribute          | Description                                      | Required | Business Validation                     | Example                  |
|--------------------|--------------------------------------------------|----------|-----------------------------------------|--------------------------|
| Title              | Title of the resource                            | Yes      | -                                       | "Introduction to Python" |
| Description        | Description of the resource                      | No       | -                                       | "Lecture notes and..."   |
| File Reference or Link | Reference to the resource file or external link | No       | -                                       | -                        |

### Timetable
| Attribute          | Description                                      | Required | Business Validation                     | Example                  |
|--------------------|--------------------------------------------------|----------|-----------------------------------------|--------------------------|
| Title              | Title or name of the timetable                   | Yes      | -                                       | "Spring 2026 Timetable"  |
| Description        | Description of the timetable                     | No       | -                                       | "Weekly class schedule"  |
| Schedule Period    | Time period covered by the timetable             | No       | -                                       | "Jan - May 2026"         |

### Gallery Album
| Attribute          | Description                                      | Required | Business Validation                     | Example                  |
|--------------------|--------------------------------------------------|----------|-----------------------------------------|--------------------------|
| Title              | Title of the gallery album                       | Yes      | -                                       | "Campus Life 2025"       |
| Description        | Description of the album                         | No       | -                                       | "Photos from various..." |

### Gallery Image
| Attribute          | Description                                      | Required | Business Validation                     | Example                  |
|--------------------|--------------------------------------------------|----------|-----------------------------------------|--------------------------|
| Title              | Title or caption of the image                    | No       | -                                       | "Annual Day Celebration" |
| Description        | Description of the image                         | No       | -                                       | -                        |
| Image Reference    | Reference to the image file                      | Yes      | -                                       | -                        |

### Academic Calendar
| Attribute          | Description                                      | Required | Business Validation                     | Example                  |
|--------------------|--------------------------------------------------|----------|-----------------------------------------|--------------------------|
| Title              | Title of the academic calendar                   | Yes      | -                                       | "Academic Year 2025-26"  |
| Description        | Description of the calendar                      | No       | -                                       | "Important academic dates" |
| Academic Year or Term | Year or term the calendar covers              | No       | -                                       | "2025-2026"              |

### Help Center Article
| Attribute          | Description                                      | Required | Business Validation                     | Example                  |
|--------------------|--------------------------------------------------|----------|-----------------------------------------|--------------------------|
| Title              | Title of the help article                        | Yes      | -                                       | "How to Register"        |
| Content            | Content of the article                           | Yes      | -                                       | "Step-by-step guide..."  |
| Category           | Category or section of the article               | No       | -                                       | "Registration"           |

### Settings
| Attribute          | Description                                      | Required | Business Validation                     | Example                  |
|--------------------|--------------------------------------------------|----------|-----------------------------------------|--------------------------|
| Key                | Unique identifier for the setting                | Yes      | Must be unique within its scope         | "theme_color"            |
| Value              | Value of the setting                             | Yes      | -                                       | "#003366"                |
| Scope              | Level at which the setting applies (College or Department) | Yes | Must be either College or Department   | "Department"             |

### Audit Log
| Attribute          | Description                                      | Required | Business Validation                     | Example                  |
|--------------------|--------------------------------------------------|----------|-----------------------------------------|--------------------------|
| Action Type        | Type of action performed                         | Yes      | -                                       | "Update Announcement"    |
| Timestamp          | Date and time of the action                      | Yes      | -                                       | -                        |
| Performed By       | Administrator who performed the action           | Yes      | -                                       | -                        |
| Affected Object Reference | Reference to the affected object           | No       | -                                       | -                        |
| Additional Details | Extra information about the action               | No       | -                                       | -                        |

### Role
| Attribute          | Description                                      | Required | Business Validation                     | Example                  |
|--------------------|--------------------------------------------------|----------|-----------------------------------------|--------------------------|
| Name               | Name of the role                                 | Yes      | Must be unique                          | "Department Admin"       |
| Description        | Description of the role                          | No       | -                                       | "Manages department content" |

### Permission
| Attribute          | Description                                      | Required | Business Validation                     | Example                  |
|--------------------|--------------------------------------------------|----------|-----------------------------------------|--------------------------|
| Name               | Name of the permission                           | Yes      | Must be unique                          | "Manage Announcements"   |
| Description        | Description of the permission                    | No       | -                                       | "Create, edit, publish announcements" |

### Department Administrator
| Attribute          | Description                                      | Required | Business Validation                     | Example                  |
|--------------------|--------------------------------------------------|----------|-----------------------------------------|--------------------------|
| Name               | Full name of the administrator                   | Yes      | -                                       | "John Doe"               |
| Email              | Email address                                    | Yes      | Must be unique                          | "john.doe@abc.edu"       |
| Assigned Departments | Departments the administrator manages         | Yes      | At least one department required        | -                        |

### Super Administrator
| Attribute          | Description                                      | Required | Business Validation                     | Example                  |
|--------------------|--------------------------------------------------|----------|-----------------------------------------|--------------------------|
| Name               | Full name of the administrator                   | Yes      | -                                       | "Admin User"             |
| Email              | Email address                                    | Yes      | Must be unique                          | "admin@abc.edu"          |

## 4. Common Metadata

The following conceptual attributes are applicable to most persistent data objects:

- **Unique Identifier**: A system-generated identifier that uniquely identifies each record.
- **Created Date**: The date and time when the record was first created.
- **Last Modified Date**: The date and time when the record was last updated.
- **Lifecycle Status**: The current state of the object in its business lifecycle (e.g., Draft, Published, Archived, Active, Inactive). Applicable to publishable entities.

## 5. Business Validation Summary

- Names of College, Department, Role, and Permission must be unique within their respective scopes.
- A Faculty Member must belong to exactly one Department.
- An Announcement must belong to either one Department or the College.
- A Gallery Image must belong to exactly one Gallery Album.
- Settings keys must be unique within their scope (College or Department).
- A Department Administrator must be assigned to at least one Department.
- Important administrative actions must be recorded in Audit Logs.
- Publishable content must follow defined lifecycle states before becoming publicly visible.

## 6. Open Questions

- Should Help Center Articles support multiple categories or tags?
- Should Audit Logs capture before-and-after values for changes?
- Are there any additional attributes required for Faculty Member (such as designation or research interests) that should be included?

---

**Document Version**: 1.0  
**Status**: Draft  
**Last Updated**: 2026-07-23  
**Depends On**: DOMAIN_MODEL.md, DATABASE_DESIGN.md, ENTITY_RELATIONSHIP_DIAGRAM.md  
**Referenced By**: Future implementation documents