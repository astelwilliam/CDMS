# CDMS — AI Development Context

> **Purpose:** This file gives AI coding assistants the context, boundaries, and rules for working on CDMS. For system design details, see [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md). For setup and run instructions, see the [`README.md`](../README.md).

## 1. Project Overview

**CDMS (Campus Department Management System)** is a web-based application for managing college information and department-level operations.

The planned system includes:

* College and department management
* Faculty member records
* Announcements and events
* Academic resources and timetables
* Academic calendar
* Gallery albums and images
* Help-center content
* User authentication and role-based administration
* Administrative audit logs

**Project status:** Early development and not production-ready. The backend foundation exists, but authorization enforcement, automated tests, security hardening, and much of the frontend are still incomplete.

Don't assume a model, endpoint, or feature is fully implemented just because it appears in the project structure or documentation.

## 2. Technology Stack

| Component             | Technology                      |
| --------------------- | ------------------------------- |
| Backend API           | FastAPI                         |
| Data validation       | Pydantic                        |
| ORM                   | SQLAlchemy                      |
| Database              | PostgreSQL                      |
| Schema migrations     | Alembic                         |
| Authentication        | JWT and password hashing        |
| Frontend              | React and Vite                  |
| HTTP client           | Axios                           |
| Backend testing tools | pytest and related dependencies |

Check the actual dependency files before adding or upgrading packages.

## 3. Repository Boundaries

The active directories are:

* `backend/`: FastAPI backend
* `frontend/`: React frontend
* `docs/`: project documentation
* `ai/`: AI development context and workflow instructions

The backend application is under `backend/app/`:

* `api/routers/`: API endpoints
* `api/schemas/`: request and response schemas
* `api/deps/`: shared dependencies, including authentication and database dependencies
* `services/`: application-level operations
* `repositories/`: database access abstractions
* `models/`: SQLAlchemy models
* `db/`: database setup and session management
* `core/`: configuration, logging, and security utilities
* `main.py`: FastAPI app setup and router registration

### Legacy or Duplicate Files

These root-level paths may be legacy or duplicate artifacts:

* `app/`
* `alembic/`
* `alembic.ini`
* `requirements.txt`
* `backend_complete.zip`

**Don't delete, move, or modify these files just to simplify the repository.** First inspect their callers, configuration references, scripts, and purpose. Put new application code in `backend/` or `frontend/` unless a verified requirement says otherwise.

## 4. Architecture Principles

The intended request flow is:

`Router → Service → Repository → Database`

Not every endpoint follows this pattern yet. Inspect the relevant code before assuming a layer exists or adding new abstractions.

Principles:

1. Keep HTTP request handling separate from business rules where the existing architecture allows it.
2. Use the existing models, schemas, repositories, and services before introducing alternatives.
3. Reuse the shared authentication and database dependencies where appropriate.
4. Avoid duplicating business logic across routers.
5. Don't refactor unrelated modules as part of a small feature or bug fix.
6. Preserve existing API behavior unless the task explicitly requires a change.
7. Document architectural decisions when a change affects multiple modules.

Don't claim a module follows the full layered architecture without inspecting its code.

## 5. Database and Migrations

PostgreSQL is the application database. Alembic is the schema migration system, configured under `backend/alembic/`.

Rules:

* Inspect the relevant SQLAlchemy model and existing migrations before changing a schema.
* Use Alembic migrations for all tracked schema changes.
* Don't use `Base.metadata.create_all()` or `create_tables.py` as a replacement for the migration workflow.
* Check foreign keys, nullability, uniqueness, relationships, and deletion behavior before changing models.
* Verify ID generation for each relevant model. Don't assume a UUID primary-key column generates its value automatically.
* Keep ORM models, Pydantic schemas, and migrations consistent.
* Don't casually modify a migration that has already been applied. Decide on the correct migration strategy first.

Run migrations from `backend/` with the correct database configuration:

```bash
alembic upgrade head
```

Confirm the college–department relationship and the ownership of other domain entities against the current models and migrations before making schema assumptions.

## 6. Authentication and Authorization

The project includes JWT-based authentication plus role-related models and dependencies.

Intended roles:

| Role                     | Intended scope                                    |
| ------------------------ | ------------------------------------------------- |
| Super Administrator      | College-level administration across departments   |
| Department Administrator | Administration limited to the assigned department |
| Public Visitor           | Access to content intended for public viewing     |

**Important:** Authentication doesn't guarantee authorization. Role-based access control is not yet consistently enforced across CRUD endpoints.

When modifying an endpoint:

1. Decide whether authentication is required.
2. Decide which roles are permitted.
3. Verify the user's college and department scope.
4. Check ownership and resource-level access, not just the role name.
5. Make sure unauthorized requests fail safely.
6. Add tests for unauthenticated, unauthorized, and authorized requests.

Never assume a router is protected just because authentication dependencies exist elsewhere in the codebase.

## 7. Security Rules

* Never commit `.env` files, passwords, private keys, or production secrets.
* Use the configuration variable names expected by `backend/app/core/config.py`.
* Never log passwords, password hashes, JWTs, access tokens, or other sensitive authentication data.
* Don't hard-code production credentials.
* Treat `seed_admin.py` as a development-only script until secure administrator provisioning is implemented.
* Don't disable authentication or authorization to make tests pass.
* Validate user input, and handle errors without exposing internal details.
* Review CORS, debug settings, secret management, and database permissions before deployment.
* Don't claim the application is production-ready without evidence from the implementation and from security testing.

## 8. Known Development Risks

Earlier repository reviews found the following items. Recheck the current branch before changing their status.

* **RBAC:** Authorization isn't consistently enforced across CRUD endpoints.
* **Password change:** An earlier implementation had an undefined `login_data` reference and logged sensitive data. Verify whether this is fixed and add regression tests.
* **Model ID defaults:** Some models appeared to have no UUID defaults. Inspect the current models and migrations, and test record creation.
* **Automated tests:** The repository previously had no substantial automated test suite.
* **Administrator provisioning:** The development seed script contains hard-coded credentials.
* **Legacy artifacts:** Root-level files may overlap with the active backend.
* **Domain relationships:** Confirm college-level versus department-level ownership using models, foreign keys, and migrations.

Don't mark an issue as resolved based only on documentation changes. Resolution requires code inspection and passing tests.

## 9. Development Workflow

For each task:

1. **Inspect:** Read the relevant source files, tests, schemas, models, and migrations.
2. **Define:** Identify the expected behavior and the smallest suitable change.
3. **Test first:** Where practical, add or update a test that captures the expected behavior.
4. **Implement:** Make a focused change that fits the existing architecture.
5. **Validate:** Run targeted tests and any relevant broader checks.
6. **Review:** Check security, error handling, compatibility, and unintended changes.
7. **Document:** Update the relevant documentation when behavior or architecture changes.
8. **Report:** State what changed, which commands and tests ran, what passed or failed, and what is still unverified.

Never report a test as passing unless it was actually run and passed.

If tests can't be run, explain why, and keep code-inspection findings separate from runtime verification.

## 10. Dependency and Environment Rules

* Backend dependencies are managed in `backend/requirements.txt`.
* Frontend dependencies are managed in `frontend/package.json` and its lockfile, if present.
* Keep dependency changes minimal, and explain why any new dependency is needed.
* Check the installed Python and Node.js versions against the project's requirements.
* Don't overwrite the user's environment or configuration without a clear reason.
* Keep local configuration and generated files out of commits where appropriate.

## 11. Scope and Change Discipline

Unless the task explicitly requires otherwise:

* Don't rewrite the whole application to implement a small feature.
* Don't migrate the frontend to another framework.
* Don't create a second authentication, database, or configuration system.
* Don't delete legacy files without analyzing their dependencies.
* Don't invent API endpoints, environment variables, model fields, or relationships.
* Don't mark planned features as implemented.
* Don't make unrelated changes to formatting, dependencies, or architecture.

When requirements are ambiguous, inspect the code and existing documentation first. Ask for clarification when the ambiguity affects security, data integrity, or a significant architectural decision.

## 12. Source of Truth

Resolve implementation questions using these sources, in this order:

1. Current source code and configuration in the active directories
2. Current Alembic migrations and database definitions
3. Tests that actually run against the current implementation
4. Current project documentation
5. Older plans, archived code, embedded ZIP files, and assumptions

If these sources conflict, explain the discrepancy instead of silently picking one.

## 13. Completion Criteria

A task is complete only when:

* The change meets the stated requirement.
* The related code follows existing project conventions.
* Relevant tests have been run, or their limitations are clearly reported.
* Security and data-integrity implications have been considered.
* Documentation has been updated where necessary.
* Unrelated files and behavior haven't been changed unnecessarily.
* The final report separates verified results from assumptions and remaining work.
