# CDMS Development Roadmap

**Project:** Campus Department Management System
**Status:** Early development — not production-ready

> Mark items `[x]` only after implementation **and** verification against the current branch's source code and tests. Use `(needs recheck)` for items reported working earlier but not yet re-verified.

> Phases are mostly sequential, but Phase 3 frontend work may run in parallel with Phase 2 for modules whose backend is complete. Phase 1 security work must be done before any module is considered complete.

Related docs: [README](../README.md) · [Architecture](ARCHITECTURE.md) · [AI Instructions](../ai/AI_INSTRUCTIONS.md)

## Phase 0 — Repository Cleanup and Baseline

* [ ] Inspect root-level `app/`, `alembic/`, `alembic.ini`, `requirements.txt`, and `backend_complete.zip` for active dependencies.
* [ ] Archive or remove confirmed legacy and duplicate files safely.
* [ ] Remove unintended test or placeholder data, such as a college named `"string"`.
* [ ] Confirm consistent project naming across application configuration and documentation.
* [ ] Add or verify `.env.example` with non-secret placeholders matching `backend/app/core/config.py`.
* [ ] Verify `.env` and other secret-bearing files are excluded through `.gitignore`.
* [ ] Verify README setup instructions work from a clean clone.
* [ ] Establish a baseline by running available checks and recording existing failures.

**Exit criteria:** The active project structure and setup process are documented and verified, configuration is handled safely, and existing issues are recorded.

## Phase 1 — Core Backend and Security

* [ ] College CRUD (needs recheck — previously verified through Swagger).
* [ ] Department CRUD (needs recheck — creation via Swagger in progress).
* [ ] Course model, migration, and CRUD endpoints.
* [ ] Verify login and credential validation.
* [ ] Verify JWT issuance, expiration, and token validation.
* [ ] Verify the current-user dependency.
* [ ] Fix password change logic.
* [ ] Verify database ID generation and model defaults.
* [ ] Enforce role-based access control for Super Administrators and Department Administrators.
* [ ] Enforce resource-level scope so Department Administrators can access only their authorized department resources.
* [ ] Add audit logging for relevant administrative actions.
* [ ] Verify validation and consistent error responses.
* [ ] Add automated tests for authentication, authorization, and core CRUD.

**Exit criteria:** Protected endpoints enforce authentication, role permissions, and resource scope. Relevant automated tests pass.

## Phase 2 — Content Modules

Implement each module using the established backend conventions (router → service → repository), migrations where required, permissions, validation, and tests.

* [ ] Faculty Members
* [ ] Announcements
* [ ] Events
* [ ] Academic Resources
* [ ] Timetables
* [ ] Academic Calendar
* [ ] Gallery Albums and Images
  * [ ] Decide on file storage and upload validation.
* [ ] Help Center
* [ ] Settings

**Exit criteria:** Each module has verified CRUD operations, appropriate authorization, documented API behavior, and tests for its critical functionality.

## Phase 3 — Frontend

* [ ] Prototype: Colleges with nested Departments (needs recheck — previously reported implemented).
* [ ] Fix stray list-marker styling on the Colleges list.
* [ ] Add department creation form.
* [ ] Establish application routing and shared page layout.
* [ ] Split the prototype into reusable components.
* [ ] Build public-facing website pages.
* [ ] Implement administrator login and session handling.
* [ ] Build the administration dashboard.
* [ ] Add create, read, update, and delete forms for supported modules.
* [ ] Add loading states, validation messages, and error handling.
* [ ] Verify frontend access restrictions and API integration.

**Exit criteria:** The frontend supports the implemented workflows and handles successful responses, validation errors, authentication failures, and loading states correctly.

## Phase 4 — Hardening and Deployment

* [ ] Review input validation and file-upload restrictions.
* [ ] Add appropriate rate limiting to sensitive endpoints.
* [ ] Restrict CORS to the required origins.
* [ ] Verify production configuration and secret management.
* [ ] Remove or restrict `seed_admin.py` for production use.
* [ ] Review authentication, authorization, and sensitive-data logging.
* [ ] Add or complete deployment scripts and instructions.
* [ ] Verify database migrations in a clean environment.
* [ ] Run the relevant automated test suite.
* [ ] Document backup, recovery, and operational requirements.

**Exit criteria:** Deployment and security checks are documented and verified for the intended environment.

## Future Scope

Features not yet approved for the initial release remain outside the committed scope until requirements are defined.
