# FastAPI API Specification

**Status**: Draft  
**Document Version**: 1.0  
**Last Updated**: 2026-07-23  
**Depends On**: DOMAIN_MODEL.md, SERVICE_LAYER_DESIGN.md, AUTHENTICATION_AND_RBAC_DESIGN.md  
**Referenced By**: PYDANTIC_SCHEMA_SPECIFICATION.md

## 1. Purpose
This document defines the REST API structure and standards for Version 1 of the Campus Department Management System (CDMS). It establishes consistent patterns for resource access, request handling, and response formatting in alignment with the approved business domain and service layer.

## 2. API Design Principles

### REST
The API follows RESTful principles with resource-oriented URLs and standard HTTP methods.

### Consistency
All endpoints follow consistent naming, structure, and behavior patterns.

### Versioning
The API uses URL-based versioning (e.g., `/api/v1/...`).

### Statelessness
Each request contains all necessary information. The server does not maintain client session state between requests.

### Pagination
List endpoints support pagination to manage large result sets efficiently.

### Filtering
List endpoints support filtering to allow clients to narrow results based on business criteria.

### Sorting
List endpoints support sorting to allow clients to order results.

## 3. API Structure

### Authentication
- Login endpoint for administrators
- Token refresh (if applicable)
- Logout endpoint

### College
- Retrieve college profile
- Update college profile (Super Administrator only)

### Departments
- List departments
- Retrieve department
- Create department (Super Administrator)
- Update department
- Delete department (Super Administrator)

### Faculty
- List faculty members (public + admin)
- Retrieve faculty member
- Create faculty member
- Update faculty member
- Soft delete / restore faculty member

### Announcements
- List announcements (public + admin)
- Retrieve announcement
- Create announcement
- Update announcement
- Publish / Archive announcement
- Soft delete / restore announcement

### Events
- List events (public + admin)
- Retrieve event
- Create event
- Update event
- Soft delete / restore event
- Manage event-gallery associations

### Academic Resources
- List resources (public + admin)
- Retrieve resource
- Create resource
- Update resource
- Soft delete / restore resource

### Timetables
- List timetables (public + admin)
- Retrieve timetable
- Create timetable
- Update timetable
- Soft delete / restore timetable

### Gallery
- List gallery albums (public + admin)
- Retrieve album with images
- Create album
- Update album
- Soft delete / restore album
- Manage images within albums

### Academic Calendar
- List calendars (public + admin)
- Retrieve calendar
- Create calendar
- Update calendar
- Soft delete / restore calendar

### Help Center
- List articles (public + admin)
- Retrieve article
- Create article
- Update article
- Soft delete / restore article

### Settings
- Retrieve settings (by scope)
- Update settings

### Roles & Permissions
- List roles
- List permissions
- Assign permissions to roles (Super Administrator)

### Administrators
- List department administrators
- Create department administrator
- Update department administrator
- Assign departments to administrator
- List super administrators
- Create super administrator

### Audit Logs
- List audit logs (Super Administrator)
- Retrieve audit log details

## 4. Request Lifecycle
1. Request received at API layer
2. Authentication and authorization verification
3. Input validation using Pydantic schemas
4. Business operation delegated to Service Layer
5. Response formatted and returned to client

## 5. Response Standards

### Success
Successful responses return appropriate HTTP status codes (200, 201, 204) with consistent JSON structure containing data and metadata.

### Validation Errors
Validation failures return 422 status with structured error details.

### Authentication Errors
Authentication failures return 401 status.

### Authorization Errors
Authorization failures return 403 status.

### Server Errors
Unexpected server errors return 500 status with minimal client-facing information.

## 6. Pagination Strategy
List endpoints return paginated results with metadata including total count, current page, page size, and links to next/previous pages.

## 7. Filtering Strategy
Filtering is supported through query parameters on list endpoints. Filters are applied at the repository level through the Service Layer.

## 8. Sorting Strategy
Sorting is supported through query parameters. Default sort order is defined per resource (typically by creation date or name).

## 9. File Upload Strategy
File uploads (for gallery images, faculty profiles, resources) are handled through dedicated endpoints or multipart form data, with references stored in the database.

## 10. API Versioning
All endpoints are prefixed with `/api/v1/`. Future versions will use `/api/v2/` while maintaining backward compatibility where possible.

## 11. Error Handling
Errors are returned in a consistent format with appropriate HTTP status codes. Business errors from the Service Layer are mapped to suitable API responses.

## 12. Best Practices
- Use plural resource names in URLs.
- Return meaningful HTTP status codes.
- Keep response payloads consistent.
- Support pagination, filtering, and sorting on all list endpoints.
- Version the API from the beginning.
- Document all endpoints clearly.

## 13. Open Questions
- Should file uploads be handled through a separate media service or directly in the API?
- Is there a need for bulk operations in Version 1?
- Should search be implemented as a dedicated endpoint or through filtering?