# My-Library API

Flask backend for a simple library management API using the app factory pattern, SQLAlchemy, Marshmallow, JWT authentication, and Redis-backed rate limiting with Flask-Limiter.

## Features

- App factory architecture with `create_app()`
- Blueprint-based route organization
- SQLAlchemy models for members, books, and loans
- Marshmallow request validation and serialization
- JWT login and refresh endpoints
- Redis-backed shared rate limiting
- JSON `429` responses when rate limits are exceeded

## Tech Stack

- Python 3.13
- Flask 3.1
- Flask-SQLAlchemy
- Marshmallow / Flask-Marshmallow
- Flask-JWT-Extended
- Flask-Limiter
- Redis
- MySQL

## Project Structure

```text
My-Library/
|-- app.py
|-- config.py
|-- requirements.txt
|-- README.md
`-- app/
    |-- __init__.py
    |-- extensions.py
    |-- models.py
    `-- blueprints/
        |-- auth/
        |   |-- __init__.py
        |   |-- routes.py
        |   `-- schemas.py
        |-- books/
        |   |-- __init__.py
        |   |-- routes.py
        |   `-- schemas.py
        |-- loans/
        |   |-- __init__.py
        |   |-- routes.py
        |   `-- schemas.py
        `-- members/
            |-- __init__.py
            |-- routes.py
            `-- schemas.py
```

## Data Model

### Member

- `id`: integer primary key
- `name`: string, required
- `email`: string, required, unique
- `DOB`: date, optional
- `password`: string, required, stored hashed for newly created or updated members

### Book

- `id`: integer primary key
- `title`: string, required
- `author`: string, required
- `genre`: string, required
- `desc`: string, required

### Loan

- `id`: integer primary key
- `loan_date`: date
- `member_id`: foreign key to `members.id`
- `book_ids`: virtual API field used to attach books to a loan

## Configuration

The app supports `DevelopmentConfig`, `TestingConfig`, and `ProductionConfig` from `config.py`.

### Environment Variables

| Variable | Required | Purpose | Example |
|---|---|---|---|
| `DATABASE_URL` | Yes | SQLAlchemy database connection string | `mysql+mysqlconnector://root:password@localhost/library_db` |
| `JWT_SECRET_KEY` | Yes | Secret used to sign JWTs. Use a strong value in production. | `super-long-random-secret-at-least-32-bytes` |
| `REDIS_URL` | Recommended | Redis connection string used by the rate limiter | `redis://localhost:6379/0` |
| `RATELIMIT_STORAGE_URI` | Optional | Explicit Flask-Limiter storage URI. Overrides `REDIS_URL` if set. | `redis://localhost:6379/1` |
| `TEST_DATABASE_URL` | Optional | Database URL for `TestingConfig` | `sqlite+pysqlite:///:memory:` |

### Default Rate Limit Settings

These values currently come from `config.py`:

- Global default limits: `200 per day, 50 per hour`
- Application-wide limit: `1000 per hour`
- In-memory fallback limits: `200 per day, 50 per hour`
- Auth login limit: `5 per minute`
- Auth refresh limit: `10 per minute`
- Heavy read endpoints: `20 per minute`
- Search endpoint: `10 per minute`

## Rate Limiting

Rate limiting is configured in `app/extensions.py` with Flask-Limiter and Redis storage.

- Authenticated requests are keyed by JWT identity: `user:<id>`
- Anonymous requests fall back to IP address: `ip:<remote_addr>`
- Rate limit headers are enabled
- `DevelopmentConfig` and `TestingConfig` automatically fall back to in-memory storage if Redis is unavailable
- Limit breaches return JSON instead of HTML

Example `429` response:

```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded. Please retry later.",
  "details": {
    "limit": "5 per 1 minute",
    "remaining": 0,
    "reset_at": "2026-03-13T15:13:09+00:00",
    "path": "/auth/login"
  }
}
```

## Authentication

JWT support is provided by Flask-JWT-Extended.

- `POST /auth/login` returns an access token and refresh token
- `POST /auth/refresh` requires a valid refresh token and returns a new access token

Note: the current codebase only enforces JWT on `/auth/refresh`. Resource endpoints for members, books, and loans are not yet protected with `@jwt_required()`.

## Setup

### 1. Create and activate a virtual environment

PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Start Redis

Use your local Redis service, or start one with Docker:

```powershell
docker run --name my-library-redis -p 6379:6379 redis:7
```

### 4. Set environment variables

PowerShell example:

```powershell
$env:DATABASE_URL = "mysql+mysqlconnector://root:password@localhost/library_db"
$env:JWT_SECRET_KEY = "replace-this-with-a-strong-random-secret"
$env:REDIS_URL = "redis://localhost:6379/0"
```

### 5. Run the application

```powershell
python app.py
```

The app starts in development mode and creates database tables automatically through `db.create_all()` in `app.py`.

Default local URL:

```text
http://127.0.0.1:5000
```

## API Endpoints

### Auth

| Method | Endpoint | Description | Rate Limit |
|---|---|---|---|
| `POST` | `/auth/login` | Authenticate a member and return JWT tokens | `5 per minute` |
| `POST` | `/auth/refresh` | Exchange a refresh token for a new access token | `10 per minute` |

#### `POST /auth/login`

Request body:

```json
{
  "email": "alice@example.com",
  "password": "secret123"
}
```

Response:

```json
{
  "access_token": "<jwt>",
  "refresh_token": "<jwt>",
  "token_type": "Bearer"
}
```

#### `POST /auth/refresh`

Headers:

```text
Authorization: Bearer <refresh-token>
```

Response:

```json
{
  "access_token": "<jwt>",
  "token_type": "Bearer"
}
```

### Members

| Method | Endpoint | Description | Rate Limit |
|---|---|---|---|
| `POST` | `/members/` | Create a new member | Default global limits |
| `GET` | `/members/` | List all members | `20 per minute` |
| `GET` | `/members/<member_id>` | Get one member | Default global limits |
| `PUT` | `/members/<member_id>` | Update a member | Default global limits |
| `DELETE` | `/members/<member_id>` | Delete a member | Default global limits |

Create member request:

```json
{
  "name": "Alice Reader",
  "email": "alice@example.com",
  "DOB": "1995-04-15",
  "password": "secret123"
}
```

Example response:

```json
{
  "DOB": "1995-04-15",
  "email": "alice@example.com",
  "id": 1,
  "name": "Alice Reader"
}
```

### Books

| Method | Endpoint | Description | Rate Limit |
|---|---|---|---|
| `POST` | `/books/` | Create a book | Default global limits |
| `GET` | `/books/` | List all books | `20 per minute` |
| `GET` | `/books/search?q=<term>` | Search title, author, genre, or description | `10 per minute` |
| `GET` | `/books/<book_id>` | Get one book | Default global limits |
| `PUT` | `/books/<book_id>` | Update a book | Default global limits |
| `DELETE` | `/books/<book_id>` | Delete a book | Default global limits |

Create book request:

```json
{
  "title": "The Pragmatic Programmer",
  "author": "Andrew Hunt",
  "genre": "Software Engineering",
  "desc": "A practical guide to software craftsmanship."
}
```

### Loans

| Method | Endpoint | Description | Rate Limit |
|---|---|---|---|
| `POST` | `/loans/` | Create a loan and attach books | Default global limits |
| `GET` | `/loans/` | List all loans | `20 per minute` |
| `GET` | `/loans/<loan_id>` | Get one loan | Default global limits |
| `PUT` | `/loans/<loan_id>` | Update a loan | Default global limits |
| `DELETE` | `/loans/<loan_id>` | Delete a loan | Default global limits |

Create loan request:

```json
{
  "loan_date": "2026-03-13",
  "member_id": 1,
  "book_ids": [1, 2]
}
```

Example loan response:

```json
{
  "book_ids": [1, 2],
  "id": 1,
  "loan_date": "2026-03-13",
  "member_id": 1
}
```

## Common Error Responses

### Invalid JSON

```json
{
  "error": "Request body must be valid JSON."
}
```

### Validation Error

Marshmallow returns field-level validation messages:

```json
{
  "email": [
    "Not a valid email address."
  ]
}
```

### Duplicate Member Email

```json
{
  "error": "Email already associated with an account."
}
```

### Not Found

```json
{
  "error": "Book not found."
}
```

## Development Notes

- `app.py` calls `db.create_all()` automatically on startup
- `TestingConfig` uses in-memory SQLite and `memory://` rate-limit storage
- `My-Library.postman_collection.json` can be used for API testing
- Passwords are hidden from serialized member responses

## Production Notes

- Replace the default `JWT_SECRET_KEY`
- Use a real MySQL database and a reachable Redis instance
- In-memory fallback is enabled for development and testing only; production should keep Redis available
- Do not rely on `db.create_all()` for schema changes in a production workflow; use migrations
- Add `@jwt_required()` to resource routes if you want JWT protection across the API
