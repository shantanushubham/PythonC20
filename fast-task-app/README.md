# Fast Task App

A FastAPI task management API with JWT authentication and PostgreSQL. Users can sign up, log in, and manage their own tasks.

## Tech Stack

- **FastAPI** — API framework
- **SQLAlchemy** — ORM
- **PostgreSQL** — Database
- **Alembic** — Migrations
- **JWT + bcrypt** — Authentication
- **uv** — Dependency management

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Docker (for PostgreSQL)

## Setup

1. **Clone and enter the project**

   ```bash
   cd fast-task-app
   ```

2. **Create environment file**

   ```bash
   cp .env.example .env
   ```

   Or create a `.env` file with:

   ```env
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=fast_task_app
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5433

   DATABASE_URL=postgresql+psycopg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}
   ```

3. **Install dependencies**

   ```bash
   uv sync
   ```

4. **Start PostgreSQL**

   ```bash
   docker compose up -d
   ```

5. **Run migrations**

   ```bash
   uv run alembic upgrade head
   ```

## Running the App

```bash
uv run uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- Swagger docs: http://127.0.0.1:8000/docs

### Debugging in Cursor / VS Code

Use the **"FastAPI: uv run uvicorn --reload"** launch configuration from the Run and Debug panel (F5).

## API Endpoints

### Auth

| Method | Endpoint       | Auth | Description        |
|--------|----------------|------|--------------------|
| POST   | `/auth/signup` | No   | Register a user    |
| POST   | `/auth/login`  | No   | Log in and get JWT |

### Tasks

All task endpoints require a `Bearer` token in the `Authorization` header. Users can only access their own tasks.

| Method | Endpoint          | Description              |
|--------|-------------------|--------------------------|
| POST   | `/tasks`          | Create a task            |
| GET    | `/tasks`          | List your tasks          |
| GET    | `/tasks/{task_id}`| Get a task               |
| PATCH  | `/tasks/{task_id}`| Update a task            |
| DELETE | `/tasks/{task_id}`| Delete a task            |

Task fields: `title`, `description`, `due_date`, `status` (`PENDING` or `FINISHED`).

### Example

```bash
# Sign up
curl -X POST http://127.0.0.1:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Jane Doe","email":"jane@example.com","password":"secret123"}'

# Create a task
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Finish report","description":"Due this week","due_date":"2026-07-25"}'
```

## Project Structure

```
app/
├── api/            # Route handlers
├── core/           # Config, database, security
├── dependencies/   # FastAPI dependencies (auth)
├── models/         # SQLAlchemy models
├── repositories/   # Database access layer
├── schemas/        # Pydantic request/response models
└── services/       # Business logic
alembic/            # Database migrations
```

## Development

```bash
# Create a new migration after model changes
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Run tests
uv run pytest
```
