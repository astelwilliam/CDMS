# Authentication and RBAC Design

**Status**: Draft  
**Document Version**: 1.0  
**Last Updated**: 2026-07-23  
**Depends On**: DOMAIN_MODEL.md, SERVICE_LAYER_DESIGN.md, REPOSITORY_LAYER_DESIGN.md  
**Referenced By**: FASTAPI_API_SPECIFICATION.md, PYDANTIC_SCHEMA_SPECIFICATION.md

## 1. Purpose
This document defines the authentication and role-based access control (RBAC) architecture for Version 1 of the Campus Department Management System (CDMS). It establishes how identity is verified and how access to resources is controlled in alignment with the approved business domain and service layer responsibilities.

## 2. Security Architecture
The security architecture separates authentication (verifying identity) from authorization (determining permissions). Authentication establishes who the user is, while authorization determines what the user is allowed to do. The architecture follows a layered approach where the API layer handles authentication, and the Service Layer enforces authorization based on roles and permissions.

## 3. Authentication Principles

### Identity
Every administrative user must have a verifiable identity within the system. Identity is established through successful authentication.

### Authentication
The process of verifying that a user is who they claim to be. Only Super Administrators and Department Administrators require authentication.

### Authorization
The process of determining what actions an authenticated user is permitted to perform based on their assigned role and permissions.

### Least Privilege
Users are granted only the minimum permissions necessary to perform their assigned responsibilities. Super Administrators have broad access, while Department Administrators have scoped access limited to their assigned department(s).

### Defense in Depth
Multiple layers of security controls are applied, including authentication, authorization, input validation, and audit logging.

## 4. User Types

### Super Administrator
Responsible for college-wide management, including:
- College profile management
- Department management
- Department Administrator management
- College-wide announcements
- System reports and audit logs
- System settings

### Department Administrator
Responsible for department-level content management, including:
- Department content (Faculty, Announcements, Events, Resources, etc.)
- Department settings
- Department-level reports

## 5. Role-Based Access Control

### Roles
Roles represent categories of users with similar responsibilities. Version 1 defines two primary roles: Super Administrator and Department Administrator.

### Permissions
Permissions represent granular rights to perform specific actions (e.g., "create_announcement", "manage_faculty", "view_audit_logs").

### Permission Assignment
Permissions are assigned to roles. Users are assigned one role, which determines their set of permissions.

### Permission Evaluation
When a user attempts an action, the system evaluates whether their role contains the required permission for that action.

### Authorization Flow
1. User authenticates and receives identity context.
2. The request reaches the Service Layer with the user's role and permissions.
3. The Service Layer checks whether the required permission exists in the user's role.
4. Access is granted or denied based on the evaluation.

## 6. Authentication Flow

### Login
An administrator provides credentials. Upon successful verification, an authentication token is issued.

### Authentication
The token is validated on subsequent requests to confirm the user's identity and role.

### Session/Token Lifecycle
Tokens have a defined validity period. Expired tokens require re-authentication.

### Logout
The user explicitly ends the session, invalidating the current token.

## 7. Password Management

### Password Storage
Passwords are stored using strong, one-way hashing algorithms. Plaintext passwords are never stored.

### Password Policy
Passwords must meet defined complexity requirements (length, character variety) to reduce the risk of compromise.

### Reset Workflow
Administrators can request password reset. A secure reset process is followed to verify identity before allowing a new password to be set.

## 8. Route Protection

### Public Endpoints
Endpoints accessible without authentication (primarily public website content such as Faculty, Announcements, Events, Gallery, etc.).

### Protected Endpoints
Endpoints that require authentication. All administrative operations fall into this category.

### Administrator-Only Endpoints
Endpoints restricted to specific roles (e.g., Super Administrator-only operations such as managing departments or viewing audit logs).

## 9. Authorization Responsibilities
The Service Layer is responsible for enforcing authorization. After authentication establishes the user's identity, the Service Layer receives the user's role and permissions and verifies that the requested business operation is permitted. Repositories and the data layer do not perform authorization checks.

## 10. Error Handling

### Authentication Failures
Invalid credentials result in authentication failure responses without revealing specific reasons that could aid attackers.

### Authorization Failures
Requests from authenticated users lacking required permissions are rejected with appropriate authorization error responses.

### Permission Failures
Attempts to perform actions without the necessary permission are logged and result in denial of access.

## 11. Security Best Practices
- Never expose internal user identifiers or permission structures to clients.
- Use secure token handling practices.
- Enforce strong password policies.
- Log all authentication and authorization events for audit purposes.
- Apply the principle of least privilege consistently.
- Separate authentication concerns from business logic.

## 12. Testing Strategy
- Test authentication flows with valid and invalid credentials.
- Verify that users can only access resources permitted by their role.
- Test permission boundaries between Super Administrator and Department Administrator roles.
- Validate that authorization checks occur at the Service Layer.
- Test token expiration and logout behavior.

## 13. Open Questions
- Should password reset tokens have a configurable expiration time?
- Is multi-factor authentication required for Super Administrators in Version 1?
- How should concurrent sessions for the same administrator be handled?