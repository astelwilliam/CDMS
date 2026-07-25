# Pydantic Schema Specification

**Status**: Draft  
**Document Version**: 1.0  
**Last Updated**: 2026-07-23  
**Depends On**: DOMAIN_MODEL.md, DATA_DICTIONARY.md, SERVICE_LAYER_DESIGN.md, FASTAPI_API_SPECIFICATION.md  
**Referenced By**: Future API implementation documents

## 1. Purpose
This document defines the Pydantic schema architecture for Version 1 of the Campus Department Management System (CDMS). It establishes standards for request validation, response serialization, and data transfer between the API layer and the Service Layer.

## 2. Schema Design Principles

### Validation
Schemas enforce data integrity at the API boundary by validating incoming requests against defined rules.

### Type Safety
Schemas provide strong typing to reduce runtime errors and improve developer experience.

### Reusability
Common schema patterns and base schemas are reused across multiple entities to reduce duplication.

### Maintainability
Schemas are organized to support long-term evolution with minimal impact on existing code.

## 3. Schema Categories

### Create Schemas
Used for creating new records. Contain only fields required or allowed during creation.

### Update Schemas
Used for updating existing records. Typically make most fields optional.

### Read Schemas
Used for returning single entity data to clients. Include all relevant fields and relationships.

### List Schemas
Used for returning collections of entities, often with reduced fields for performance.

### Response Schemas
Wrap data with metadata such as pagination information or status messages.

## 4. Entity Schemas

### College
- **Create Schema**: Fields required to create a college profile.
- **Update Schema**: Fields allowed to update the college profile.
- **Read Schema**: Full college representation including system settings reference.
- **List Schema**: Summary fields for college listing (primarily for Super Administrators).

### Department
- **Create Schema**: Fields required when creating a department.
- **Update Schema**: Fields allowed when updating a department.
- **Read Schema**: Complete department information with relationships.
- **List Schema**: Summary view for department listings.

### Faculty Member
- **Create Schema**: Fields required to add a faculty member.
- **Update Schema**: Fields allowed to update faculty information.
- **Read Schema**: Full faculty member details.
- **List Schema**: Summary fields for public and admin listings.

### Announcement
- **Create Schema**: Fields required to create an announcement.
- **Update Schema**: Fields allowed to update announcement content.
- **Read Schema**: Full announcement with lifecycle status.
- **List Schema**: Summary view for public and admin listings.

### Event
- **Create Schema**: Fields required to create an event.
- **Update Schema**: Fields allowed to update event details.
- **Read Schema**: Full event information with gallery associations.
- **List Schema**: Summary view for listings.

### Academic Resource
- **Create Schema**: Fields required to create a resource.
- **Update Schema**: Fields allowed to update resource metadata.
- **Read Schema**: Full resource representation.
- **List Schema**: Summary view for listings.

### Timetable
- **Create Schema**: Fields required to create a timetable.
- **Update Schema**: Fields allowed to update timetable.
- **Read Schema**: Full timetable representation.
- **List Schema**: Summary view for listings.

### Gallery Album
- **Create Schema**: Fields required to create an album.
- **Update Schema**: Fields allowed to update album metadata.
- **Read Schema**: Album with associated images.
- **List Schema**: Summary view for album listings.

### Gallery Image
- **Create Schema**: Fields required to add an image.
- **Update Schema**: Fields allowed to update image metadata.
- **Read Schema**: Full image representation.
- **List Schema**: Summary view for images within an album.

### Academic Calendar
- **Create Schema**: Fields required to create a calendar.
- **Update Schema**: Fields allowed to update calendar.
- **Read Schema**: Full calendar representation.
- **List Schema**: Summary view for listings.

### Help Center Article
- **Create Schema**: Fields required to create an article.
- **Update Schema**: Fields allowed to update article content.
- **Read Schema**: Full article representation.
- **List Schema**: Summary view for listings.

### Setting
- **Create Schema**: Fields required to create a setting.
- **Update Schema**: Fields allowed to update a setting.
- **Read Schema**: Full setting representation.
- **List Schema**: Summary view filtered by scope.

### Role
- **Create Schema**: Fields required to create a role.
- **Update Schema**: Fields allowed to update a role.
- **Read Schema**: Role with associated permissions.
- **List Schema**: Summary view of roles.

### Permission
- **Create Schema**: Fields required to create a permission.
- **Update Schema**: Fields allowed to update a permission.
- **Read Schema**: Full permission representation.
- **List Schema**: Summary view of permissions.

### Department Administrator
- **Create Schema**: Fields required to create an administrator account.
- **Update Schema**: Fields allowed to update administrator details.
- **Read Schema**: Administrator with assigned departments and role.
- **List Schema**: Summary view of administrators.

### Super Administrator
- **Create Schema**: Fields required to create a super administrator.
- **Update Schema**: Fields allowed to update super administrator details.
- **Read Schema**: Full super administrator representation.
- **List Schema**: Summary view of super administrators.

### Audit Log
- **Read Schema**: Full audit log entry.
- **List Schema**: Summary view of audit logs.

## 5. Validation Strategy

### Required Fields
Fields that must be present and non-empty are marked as required in Create and Update schemas.

### Optional Fields
Fields that may be omitted during creation or update are marked as optional.

### Length Constraints
String fields have maximum length limits defined according to business requirements.

### Format Validation
Fields such as email addresses follow format validation rules.

### Business Validation Boundaries
Complex business rules (e.g., lifecycle transitions, ownership validation) are enforced in the Service Layer rather than in Pydantic schemas.

## 6. Nested Schemas
Schemas for entities with relationships (e.g., Department with Faculty Members, Gallery Album with Images) may include nested schemas where appropriate for read operations. Deep nesting is avoided to prevent performance issues.

## 7. Pagination Schemas
Pagination metadata is included in list responses using a standard pagination schema containing total count, current page, page size, and navigation links.

## 8. Error Response Schemas
Error responses follow a consistent structure containing error type, message, and field-specific validation errors where applicable.

## 9. Serialization Strategy
Read schemas control exactly which fields are exposed to clients. Sensitive fields (such as password hashes or internal identifiers) are never included in response schemas.

## 10. Best Practices
- Keep schemas focused and avoid unnecessary nesting.
- Use separate schemas for Create, Update, and Read operations.
- Define validation rules close to the data definition.
- Reuse common schema components where possible.
- Maintain consistency in field naming between schemas and the data dictionary.

## 11. Open Questions
- Should schemas support partial updates using PATCH semantics in Version 1?
- Is there a need for separate admin and public read schemas for certain entities?
- How should file upload metadata be represented in schemas?