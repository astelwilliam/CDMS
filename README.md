# CDMS — Campus Department Management System

A web-based system for managing college information and department-level operations.

> **Status:** Early development. Not production-ready.

## Tech Stack

FastAPI · SQLAlchemy · PostgreSQL · Alembic · JWT authentication · React (Vite) · Axios

## Repository Structure

* `backend/`: active API code
* `frontend/`: active React application
* Root-level `app/`, `alembic/`, `alembic.ini`, `requirements.txt`, and `backend_complete.zip`: possibly legacy or duplicate files

> **Temporary precaution:** Don't change root-level files until you've checked their dependencies and usage. Put new backend and frontend work in the active directories.

## Quick Start

### 1. Create the database

Create a PostgreSQL database named `cdms` using `psql` or another PostgreSQL client.

### 2. Set up the backend

Run these commands from the repository root:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

On macOS/Linux, activate the environment with:

```bash
source venv/bin/activate
```

### 3. Configure the environment

Copy `.env.example` to `.env` inside `backend/`. Then set the database URL and `SECRET_KEY`. Check that all variable names match `backend/app/core/config.py`.

> Never commit real secrets or `.env` files.

### 4. Run database migrations

From the `backend/` directory:

```bash
alembic upgrade head
```

### 5. (Optional) Create a development administrator

From the `backend/` directory:

```bash
python seed_admin.py
```

> **Development only:** The seed script contains hard-coded credentials. Don't use it in shared or production environments.

### 6. Install frontend dependencies

Open a new terminal at the repository root:

```bash
cd frontend
npm install
```

## Running the Project

After setup, open two terminals at the repository root.

**Terminal 1: Backend**

```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

On macOS/Linux, use `source venv/bin/activate` instead of the PowerShell activation command.

* API: http://127.0.0.1:8000
* Swagger UI: http://127.0.0.1:8000/docs

**Terminal 2: Frontend**

```bash
cd frontend
npm run dev
```

* Frontend: http://localhost:5173

## Documentation

<!-- Check each path in the current branch before committing. Remove any links that don't exist yet. -->

* [AI Instructions](./ai/AI_INSTRUCTIONS.md)
* [Contributing Guide](./CONTRIBUTING.md)

## Known Gaps

* **Authorization/RBAC:** Role-based access control isn't enforced consistently across CRUD endpoints.
* **Password change:** An earlier issue involved an undefined `login_data` reference and logging of sensitive data. Check the current code and add regression tests.
* **Model ID defaults:** Check that creating records works for models that don't have ID defaults set.
* **Automated tests:** Add real tests for authentication, authorization, CRUD operations and error handling.
* **Admin provisioning:** Replace the hard-coded development credentials with a secure way to create administrators.
* **Deployment security:** Before deploying, review secret management, CORS, debug settings, authorization and database permissions.

> These items still need to be checked against the current code. Being listed here doesn't mean they've been fixed.
