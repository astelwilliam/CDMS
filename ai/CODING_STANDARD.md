# Coding Standard

## Purpose
This document defines the official coding standards, naming conventions, and engineering practices for the Campus Department Management System (CDMS). It ensures consistency, readability, maintainability, and security across all codebases.

## Table of Contents
- [1. Purpose](#1-purpose)
- [2. Scope](#2-scope)
- [3. General Engineering Principles](#3-general-engineering-principles)
- [4. Project Folder Organization](#4-project-folder-organization)
- [5. File Naming Conventions](#5-file-naming-conventions)
- [6. Variable Naming Conventions](#6-variable-naming-conventions)
- [7. Function Naming Conventions](#7-function-naming-conventions)
- [8. Class Naming Conventions](#8-class-naming-conventions)
- [9. API Naming Conventions](#9-api-naming-conventions)
- [10. Database Naming Conventions](#10-database-naming-conventions)
- [11. Commenting & Documentation Standards](#11-commenting--documentation-standards)
- [12. Error Handling Guidelines](#12-error-handling-guidelines)
- [13. Logging Standards](#13-logging-standards)
- [14. Configuration Management](#14-configuration-management)
- [15. Dependency Management](#15-dependency-management)
- [16. Security Coding Practices](#16-security-coding-practices)
- [17. Performance Guidelines](#17-performance-guidelines)
- [18. Testing Expectations](#18-testing-expectations)
- [19. Code Review Checklist](#19-code-review-checklist)
- [20. Definition of Clean Code](#20-definition-of-clean-code)

## 1. Purpose
This standard establishes consistent coding practices for the CDMS project to support long-term maintainability and collaboration.

## 2. Scope
This document applies to all code written for the CDMS project, including backend (Python/FastAPI), frontend (Flutter/Dart), database scripts, and supporting configuration files.

## 3. General Engineering Principles
- Prioritize readability and maintainability over clever or compact code.
- Follow industry-standard conventions for each technology.
- Write explicit code rather than relying on implicit behavior.
- Minimize coupling and maximize cohesion.
- Apply the principle of least astonishment.
- Security considerations must be addressed in every implementation.

## 4. Project Folder Organization
The high-level repository structure is defined in the project documentation. Detailed organization within the `backend/`, `frontend/`, and `database/` directories follows standard practices for each technology stack. **TODO**: Define specific module and package organization rules inside backend and frontend directories.

## 5. File Naming Conventions
- **Python**: Use `snake_case.py` for modules (e.g., `user_service.py`).
- **Flutter/Dart**: Use `snake_case.dart` for files (e.g., `faculty_page.dart`).
- **SQL**: Use `snake_case.sql` for migration and seed files.
- Test files should be prefixed with `test_` (Python) or suffixed with `_test.dart` (Flutter).

## 6. Variable Naming Conventions
- Use `snake_case` for Python variables.
- Use `camelCase` for Dart variables.
- Names must be descriptive and self-explanatory.
- Avoid single-letter variables except for loop counters or well-known mathematical variables.
- Constants should use `UPPER_SNAKE_CASE` (Python) or `kConstantName` (Dart).

## 7. Function Naming Conventions
- Use `snake_case` for Python functions (e.g., `get_faculty_list`).
- Use `camelCase` for Dart functions and methods (e.g., `fetchFacultyList`).
- Function names should clearly describe their purpose using verbs.
- Private functions/methods should be prefixed with an underscore (`_`).

## 8. Class Naming Conventions
- Use `PascalCase` for all class names in both Python and Dart (e.g., `FacultyService`, `DepartmentRepository`).
- Class names should be nouns or noun phrases.

## 9. API Naming Conventions
- Use RESTful resource-based URLs with plural nouns (e.g., `/api/v1/faculties`, `/api/v1/announcements`).
- Use `snake_case` for query parameters and JSON field names.
- HTTP methods must follow standard semantics (GET, POST, PUT, PATCH, DELETE).
- **TODO**: Confirm exact API versioning strategy and base path conventions.

## 10. Database Naming Conventions
- Use `snake_case` for all table names, column names, and indexes (PostgreSQL standard).
- Primary keys should be named `id`.
- Foreign keys should follow the pattern `table_name_id`.
- Use singular table names where appropriate (industry preference for PostgreSQL).
- **TODO**: Define specific rules for enum types, views, and stored procedures if used.

## 11. Commenting & Documentation Standards
- Write code that is largely self-documenting through clear naming.
- Use docstrings (Python) or dartdoc comments (Dart) for all public functions, classes, and modules.
- Comments should explain *why*, not *what*.
- Keep comments concise and up to date.
- Every file should contain a brief file-level description at the top.

## 12. Error Handling Guidelines
- Use specific exception types rather than generic ones.
- Never swallow exceptions silently.
- Return meaningful error messages to clients while logging detailed information server-side.
- Follow FastAPI’s exception handling patterns for backend.
- Use Dart’s `try-catch` with specific exception types on the frontend.
- All errors must be handled at appropriate layers.

## 13. Logging Standards
- Use structured logging where possible.
- Log at appropriate levels: DEBUG, INFO, WARNING, ERROR, CRITICAL.
- Never log sensitive data (passwords, tokens, personal information).
- Include contextual information (user ID, request ID) where applicable.
- **TODO**: Select and standardize the logging library and format for the backend.

## 14. Configuration Management
- Store configuration in environment variables or dedicated configuration files.
- Never hardcode secrets, credentials, or environment-specific values in source code.
- Use a consistent configuration loading pattern across the application.
- **TODO**: Define the official configuration management approach and file locations.

## 15. Dependency Management
- Use official package managers: `pip` + `requirements.txt` or `pyproject.toml` (backend), `pubspec.yaml` (frontend).
- Pin dependency versions for reproducibility.
- Regularly audit dependencies for security vulnerabilities.
- Avoid unnecessary third-party dependencies.

## 16. Security Coding Practices
- Validate and sanitize all user input.
- Use parameterized queries to prevent SQL injection.
- Implement proper authentication and authorization checks on every protected endpoint.
- Store passwords using strong hashing algorithms.
- Follow the principle of least privilege for database and API access.
- Protect against common vulnerabilities (OWASP Top 10).

## 17. Performance Guidelines
- Write efficient queries and avoid N+1 problems.
- Use pagination for list endpoints.
- Cache expensive operations where appropriate.
- Profile before optimizing.
- Keep response times within acceptable limits for web applications.

## 18. Testing Expectations
- Every non-trivial function and class must have unit tests.
- Integration tests are required for API endpoints and database interactions.
- Maintain high test coverage with meaningful assertions.
- Tests must be deterministic and independent.
- Follow the testing pyramid approach.

## 19. Code Review Checklist
Before requesting review, ensure:
- Code follows this standard.
- All tests pass.
- Documentation is updated.
- No sensitive data is exposed.
- Security best practices are applied.
- Code is modular and follows SOLID principles where applicable.

## 20. Definition of Clean Code
Clean code in CDMS is code that is:
- Easy to read and understand.
- Easy to modify and extend.
- Well tested and reliable.
- Secure by design.
- Consistent with the rest of the codebase.
- Free of unnecessary complexity.