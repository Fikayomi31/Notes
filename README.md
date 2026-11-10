# FastAPI Notes API

A small asynchronous REST API for user registration, JWT authentication, and user-owned notes. The application uses FastAPI, SQLAlchemy's async ORM, SQLite by default, and Alembic migrations.

## Features

- User registration and login with bcrypt password hashing.
- JWT bearer tokens with a 30-minute expiration.
- CRUD endpoints for notes, scoped to the authenticated user.
- User and note ORM models with a one-to-many relationship.
- Async SQLAlchemy sessions injected into request handlers.
- Alembic-managed database schema.
- Role-protected user and admin example endpoints.
- Interactive API documentation at `/docs` and `/redoc` when the app is running.

## Project layout

    app/
      core/
        config.py          Secret and JWT configuration
        jwt.py             Access-token creation and validation
        permissions.py     Role-based access dependency
        security.py        Password hashing and verification
      routers/
        auth.py            Registration, login, and current-user routes
        notes.py           Note CRUD routes
      database.py          Async engine, session factory, and Base
      dependencies.py      Database and authenticated-user dependencies
      main.py              FastAPI application and example role routes
      models.py            SQLAlchemy User and Note models
      schemas.py           Pydantic request and response schemas
    alembic/
      versions/            Database migration scripts
      env.py               Async Alembic configuration
    alembic.ini
    requirements.txt
    notes.db               Local SQLite database (created by migrations)

## Requirements

- Python 3.10 or newer.
- SQLite is used by default and needs no separate server.
- PostgreSQL can be used with an async SQLAlchemy URL, but its async driver is not included in `requirements.txt` (see Database configuration).

## Setup

Run these commands from the project root.

### 1. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS or Linux:

```sh
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```sh
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure the signing secret

Create a `.env` file in the project root. It is ignored by Git. Set `SECRET_KEY` to a private random value of at least 32 characters. Generate a value with:

```sh
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Put the generated value in `.env`:

```dotenv
SECRET_KEY=replace-this-with-the-generated-value
```

The application loads this file when it loads its core configuration. Do not commit real secrets.

### 4. Apply database migrations

```sh
alembic upgrade head
```

This creates or updates the database schema. With the default settings, the SQLite file is `notes.db` in the process working directory. To see the current migration revision, run:

```sh
alembic current
```

### 5. Start the API

```sh
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for Swagger UI, or `http://127.0.0.1:8000/redoc` for ReDoc.

## Configuration

| Setting | Default | Description |
| --- | --- | --- |
| `SECRET_KEY` | Required | JWT signing secret; must contain at least 32 characters. It may be loaded from the root `.env` file. |
| `DATABASE_URL` | `sqlite+aiosqlite:///./notes.db` | SQLAlchemy async database URL. Set it in the process environment before starting the app or running Alembic. |
| JWT algorithm | `HS256` | Configured in `app/core/config.py`. |
| Access-token lifetime | 30 minutes | Configured in `app/core/config.py`. |

For example, in PowerShell, set a database URL for the current terminal before running Alembic or Uvicorn:

```powershell
$env:DATABASE_URL = "sqlite+aiosqlite:///./notes.db"
```

For PostgreSQL, install an async driver and use a URL such as `postgresql+asyncpg://username:password@localhost:5432/notes`. The project currently does not pin `asyncpg`, so install it separately when using PostgreSQL:

```sh
pip install asyncpg
```

Set the `DATABASE_URL` environment variable in the same environment that runs both the migration command and the API. The project uses Alembic for schema setup; tables are not created automatically by FastAPI startup.

## Database model

### User

The `users` table stores an integer ID, unique username and email, hashed password, role, and creation timestamp. Passwords are never returned by the API. New registrations receive the `user` role.

### Note

The `notes` table stores an integer ID, title, content, creation and update timestamps, and a required `user_id` foreign key. Each note belongs to one user; a user may own multiple notes. Note list, read, update, and delete operations are restricted to the authenticated owner.

Deleting a user through the ORM cascades to that user's notes. There is no user deletion endpoint in the current API.

## Authentication and authorization

Register with `/api/auth/register`, then send the returned credentials to `/api/auth/login`. Login returns a JWT access token. Include it on protected requests as:

```http
Authorization: Bearer <access-token>
```

You can also use the **Authorize** button in Swagger UI and enter the bearer token. Tokens expire after 30 minutes. Newly registered accounts have the `user` role; the API does not currently expose an endpoint for promoting an account to `admin`.

Passwords must be between 6 and 12 characters under the current request schema. Passwords are hashed with bcrypt before they are stored.

## API endpoints

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/` | No | Welcome message. |
| `POST` | `/api/auth/register` | No | Create a user; returns `201 Created`. |
| `POST` | `/api/auth/login` | No | Validate credentials and return a bearer token. |
| `GET` | `/api/auth/me` | Yes | Return the current user's public profile. |
| `GET` | `/api/notes/` | Yes | List the current user's notes, newest first. |
| `POST` | `/api/notes/` | Yes | Create a note; returns `201 Created`. |
| `GET` | `/api/notes/{note_id}` | Yes | Read one of the current user's notes. |
| `PATCH` | `/api/notes/{note_id}` | Yes | Update the supplied title and/or content. |
| `DELETE` | `/api/notes/{note_id}` | Yes | Delete one of the current user's notes; returns `204 No Content`. |
| `GET` | `/api/user-area` | User role | Example route restricted to the `user` role. |
| `GET` | `/api/admin-area` | Admin role | Example route restricted to the `admin` role. |

### Example: register and log in

Register:

```sh
curl -X POST http://127.0.0.1:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"ChangeMe1"}'
```

Log in:

```sh
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"ChangeMe1"}'
```

The login response contains `access_token` and `token_type`. Copy the token for authenticated examples below.

### Example: create and list notes

Create a note:

```sh
curl -X POST http://127.0.0.1:8000/api/notes/ \
  -H "Authorization: Bearer <access-token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"First note","content":"A note saved in SQLite."}'
```

List the authenticated user's notes:

```sh
curl http://127.0.0.1:8000/api/notes/ \
  -H "Authorization: Bearer <access-token>"
```

### Request validation and behavior

- Registration requires a username (up to 50 characters), valid email, and a 6–12 character password.
- Note creation requires a title from 1 to 100 characters and non-empty content.
- Note titles must be unique per user, compared case-insensitively. A duplicate title returns `409 Conflict`.
- PATCH accepts `title`, `content`, or both. At least one field must be supplied. A duplicate title returns `409 Conflict`.
- A note that does not exist or belongs to a different user is returned as `404 Not Found`.
- Missing or invalid bearer credentials return `401 Unauthorized`; role mismatches return `403 Forbidden`.
- Invalid request data is rejected with FastAPI's `422 Unprocessable Content` response.

## Database migrations

Migration scripts live in `alembic/versions`. The current initial migration creates the `users` and `notes` tables. Common commands:

```sh
alembic upgrade head
alembic current
alembic history
```

After changing SQLAlchemy models, create a new migration and review it before applying it:

```sh
alembic revision --autogenerate -m "describe the schema change"
alembic upgrade head
```

Keep migration files under version control. Back up a database before applying schema changes to important data.

## Implementation notes

- `app/database.py` creates the async SQLAlchemy engine and session factory, defines the declarative base, and provides the `get_db` dependency.
- `app/models.py` defines the ORM entities and relationship.
- `app/schemas.py` defines input and output DTOs. ORM response schemas use Pydantic's `from_attributes` support.
- `app/routers/auth.py` and `app/routers/notes.py` use async sessions for database operations.
- `app/dependencies.py` resolves bearer-token users and provides the session dependency used during authentication.
- SQLite foreign-key enforcement is enabled by a connection event in `app/database.py`.

## Troubleshooting

### `SECRET_KEY environment variable is not set`

Create the root `.env` file and set `SECRET_KEY` to a random value at least 32 characters long, then restart the application.

### The database is empty or tables are missing

Run `alembic upgrade head` from the project root, using the same `DATABASE_URL` as the API process.

### PostgreSQL driver cannot be loaded

Install `asyncpg`, set a `postgresql+asyncpg://...` URL in `DATABASE_URL`, and run migrations against that database.

### The API uses a different SQLite file than expected

The default SQLite path is relative to the process working directory. Start Uvicorn and Alembic from the project root, or set an explicit database URL.
