# Instructions for AI Coding Assistants

## Context

**Project:** CDMS (Campus Department Management System)

**Stack:** FastAPI, SQLAlchemy, Alembic, PostgreSQL, Pydantic, React, Vite, Axios

**Status:** Early development. Not production-ready.

All file paths in this document are relative to the repository root.

## Before You Start

1. Read `ai/AI_CONTEXT.md` and `docs/ARCHITECTURE.md` if they exist in the current branch.
2. Look at the relevant source code, models, schemas, migrations, and tests before assuming that the documentation describes finished functionality.
3. Find the existing pattern for the area you are changing and follow it.

## Hard Rules

1. **Active application directories:** Backend work goes in `backend/`. Frontend work goes in `frontend/`. The root-level `app/`, `alembic/`, `alembic.ini`, `requirements.txt`, and `backend_complete.zip` may be legacy or duplicate files. Do not modify or delete them unless you have checked how they are used and what depends on them.

2. **Backend architecture:** Use the router → service → repository pattern for new code where it fits. Keep business logic out of routers. Keep database operations in the established data-access layer. Do not assume every module already has all three layers.

3. **Database changes:** Every tracked schema change needs an Alembic migration in `backend/`. Do not make manual database changes in place of migrations. Check the existing migration history before you generate or apply a migration.

4. **Primary keys:** Follow the existing model conventions. Check UUID column types, ID generation, defaults, and migration definitions. Do not assume every model generates UUIDs correctly.

5. **Pydantic schemas:** Keep Create, Update, and Read schemas separate where appropriate. Follow the existing naming conventions, validation rules, and response formats. Do not create a duplicate schema unless there is a reason.

6. **Secrets and configuration:** Never hard-code secrets or credentials. Read configuration through the existing settings system, using the variable names in `backend/app/core/config.py`. Never log passwords, password hashes, tokens, or other sensitive authentication data.

7. **No invented details:** Never invent model fields, API endpoints, environment variables, files, relationships, or dependencies. Read the source code first. If a requirement is still unclear, ask, or clearly mark the assumption as unresolved.

8. **Authorization and resource scope:** Administrative endpoints must enforce authentication, role permissions, and resource-level scope. Department administrators must not read or change resources outside their own department. When you change a protected endpoint, add tests for unauthenticated, unauthorized, and authorized requests.

9. **Minimal changes:** Change only what the task requires. Avoid unrelated refactoring, dependency upgrades, formatting changes, or architecture changes.

10. **Frontend conventions:** Use React functional components and hooks, following existing patterns. Send HTTP calls through the existing API client (`frontend/src/api.js`, if that is the configured client). Do not create a second API client without a clear reason.

11. **Error handling:** Validate input, handle expected failures, and return the correct HTTP status codes. Never show clients stack traces, secrets, database credentials, or internal implementation details.

12. **Tests and verification:** Add or update tests for any behavior you change, where practical. Never say tests pass unless you actually ran them and they passed. If you cannot run a test, say so clearly.

13. **Destructive and irreversible operations:** Do not drop tables, delete user data, reset databases, remove potentially active files, or rewrite migration history without first explaining the impact and obtaining explicit approval. Prefer reversible, narrowly scoped changes. Never run destructive commands against a production environment.

14. **Test limitations:** If a test cannot reasonably be added or executed, explain why. Perform other relevant checks where possible, and distinguish verified results from assumptions or untested behavior.

15. **Dependency discipline:** Do not add, remove, or upgrade dependencies unless the task requires it. Explain the purpose of each dependency change and update the appropriate dependency files.

## Output Expectations

For each coding task, provide:

1. **Files changed:** Every file you created, modified, or deleted, with its path from the repository root.
2. **Implementation:** Complete file contents or clearly marked diffs.
3. **Database changes:** Any migration required, and whether it was generated and tested.
4. **Configuration and dependencies:** Any changes needed to environment variables, dependencies, or setup.
5. **Verification:** Specific steps to check the result, such as a Swagger request at `/docs`, a frontend action, or a test command.
6. **Results:** Which checks you actually ran, what they showed, and any remaining risks or unverified assumptions.

## Decision Rule

When documentation, assumptions, and code disagree, the current source code, models, migrations, and tests are the source of truth. Explain the mismatch in your report. Do not quietly change unrelated architecture or behavior to resolve it.

## When Unsure

Stop and ask rather than guess. A clearly stated open question is better than a confident wrong change.
