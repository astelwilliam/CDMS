# CDMS — System Architecture

## 1. Overview

CDMS is a web-based Campus Department Management System with a React frontend and a FastAPI backend.

```text
React (Vite)
    |
    | HTTP / JSON (Axios)
    v
FastAPI backend
    |
    v
SQLAlchemy ORM
    |
    v
PostgreSQL
```

**Status:** Early development. The architecture and role definitions documented here do not imply that all features, security controls, or data relationships are complete.

## 2. Backend Structure

The active backend is located in `backend/app/`.

| Component       | Responsibility                                                          |
| --------------- | ----------------------------------------------------------------------- |
| `api/routers/`  | HTTP endpoints and request handling                                     |
| `api/schemas/`  | Pydantic request and response schemas                                   |
| `api/deps/`     | Shared dependencies, including database and authentication dependencies |
| `services/`     | Business operations and application-level rules                         |
| `repositories/` | Database access abstractions                                            |
| `models/`       | SQLAlchemy ORM models                                                   |
| `db/`           | Database engine, sessions, and declarative base                         |
| `core/`         | Configuration, logging, and security utilities                          |
| `main.py`       | FastAPI application setup and router registration                       |

### Request Flow

The intended architecture is:

`Router → Service → Repository → Database`

The actual implementation may differ by endpoint. The service layer is not yet consistently used throughout the application. Confirm each endpoint's dependencies and database access before treating this flow as a repository-wide rule.

## 3. Domain Model

The intended domain includes:

* Colleges
* Departments
* Faculty members
* Users
* Roles and permissions
* Announcements and events
* Academic resources and timetables
* Gallery albums and images
* Academic calendar entries
* Help-center articles
* Administrative audit logs

### Relationships to Verify

The following relationships must be confirmed against the SQLAlchemy models, foreign keys, and migration files:

* A college and its departments
* Departments and faculty members
* Whether announcements, events, academic resources, timetables, galleries, and calendar entries belong to a college, a department, or both
* User-to-role and role-to-permission associations
* Audit-log relationships to administrative users and affected records

### Primary Keys

Inspect each model and its migration to confirm:

* The primary-key column type
* Whether the database or application generates its value
* Whether a default is configured
* Whether record creation works without explicitly supplying an ID

Do not assume every model automatically generates a UUID.

## 4. Roles and Intended Scope

| Role                     | Intended scope                                       |
| ------------------------ | ---------------------------------------------------- |
| Super Administrator      | College-level administration across departments      |
| Department Administrator | Administration restricted to the assigned department |
| Public Visitor           | Access to content intended for public viewing        |

**Authorization status:** Role definitions and authentication dependencies exist, but access-control enforcement is not consistently applied across CRUD endpoints. These scopes are intended permissions, not a guarantee that every endpoint currently enforces them.

## 5. Database Migrations

The active migration configuration is under `backend/alembic/`.

Use Alembic for tracked schema changes:

```bash
alembic upgrade head
```

Run the command from the `backend/` directory with the correct database configuration.

`create_tables.py` uses SQLAlchemy table-creation functionality. Review its callers and purpose before deciding whether to retain, restrict, or remove it. Do not use separate schema-creation methods as a substitute for the established migration workflow.

## 6. Legacy and Duplicate Files

The repository contains root-level paths that may overlap with the active backend, including:

* `app/`
* `alembic/`
* `alembic.ini`
* `requirements.txt`
* `backend_complete.zip`

Their current usage must be investigated before they are modified or removed. Treat `backend/` and `frontend/` as the active application directories, while preserving root-level files until their dependencies are understood.

## 7. Known Architecture Gaps

* Role-based authorization is not consistently enforced.
* The service-layer pattern is not consistently applied.
* Model ID defaults and record creation need verification.
* Domain relationships require confirmation against models and migrations.
* Automated tests are insufficient to validate the architecture and security guarantees.
* Legacy or duplicate repository files have not been fully investigated.

Resolve these gaps incrementally and update this document when implementation and tests confirm the changes.
