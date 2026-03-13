# My Library

Flask library management app with JWT authentication, rate limiting, caching, and a browser frontend for members, books, and loans.

## Stack

- Flask 3.1
- SQLAlchemy
- Marshmallow
- Flask-JWT-Extended
- Flask-Limiter
- Flask-Caching
- MySQL
- Redis
- Vanilla JavaScript frontend
- Gunicorn for production

## Features

- App factory architecture with `create_app()`
- Blueprint-based API routes
- JWT login and refresh flow
- Redis-backed shared rate limiting
- Cached read endpoints with invalidation on writes
- Home page for member login and registration
- Dashboard for books and loans
- Railway-ready production startup with `gunicorn`

## Project Structure

```text
My-Library/
|-- app.py
|-- config.py
|-- gunicorn.conf.py
|-- railway.json
|-- requirements.txt
|-- README.md
`-- app/
    |-- __init__.py
    |-- extensions.py
    |-- models.py
    |-- templates/
    |   |-- base.html
    |   |-- home.html
    |   `-- dashboard.html
    |-- static/
    |   |-- scripts/
    |   |   |-- api.js
    |   |   |-- auth.js
    |   |   |-- dashboard.js
    |   |   |-- home.js
    |   |   `-- layout.js
    |   `-- styles/
    |       `-- app.css
    `-- blueprints/
        |-- auth/
        |-- books/
        |-- frontend/
        |-- loans/
        `-- members/
```

## Environment Variables

### Required for production

| Variable | Purpose | Example |
|---|---|---|
| `JWT_SECRET_KEY` | Signs JWT access and refresh tokens | `a-long-random-secret-value` |
| `DATABASE_URL` or Railway MySQL vars | Database connection string | `mysql://user:pass@host:3306/db` |

### Recommended for production

| Variable | Purpose | Example |
|---|---|---|
| `REDIS_URL` | Shared Redis connection for rate limiting | `redis://default:password@host:6379` |
| `CACHE_REDIS_URL` | Redis connection for Flask-Caching | `redis://default:password@host:6379/1` |
| `RATELIMIT_STORAGE_URI` | Explicit limiter storage override | `redis://default:password@host:6379/0` |
| `APP_CONFIG` | Config class override | `ProductionConfig` |

### Optional

| Variable | Purpose | Default |
|---|---|---|
| `AUTO_CREATE_TABLES` | Runs `db.create_all()` on startup when set to `true` | `false` |
| `GUNICORN_WORKERS` | Gunicorn worker count | `2` |
| `GUNICORN_THREADS` | Gunicorn threads per worker | `4` |
| `GUNICORN_TIMEOUT` | Gunicorn timeout in seconds | `120` |

## Local Development

### 1. Create a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Set local environment variables

```powershell
$env:APP_CONFIG = "DevelopmentConfig"
$env:DATABASE_URL = "mysql+mysqlconnector://root:password@localhost/library_db"
$env:JWT_SECRET_KEY = "replace-this-with-a-strong-random-secret"
$env:REDIS_URL = "redis://localhost:6379/0"
```

### 4. Run the app

```powershell
python app.py
```

Local URLs:

- Home: `http://127.0.0.1:5000/`
- Dashboard: `http://127.0.0.1:5000/dashboard`
- Healthcheck: `http://127.0.0.1:5000/health`

## Railway Deployment

This repo is configured for Railway with:

- `railway.json` start command: `gunicorn app:app`
- `gunicorn.conf.py` binding to Railway's `PORT`
- `/health` endpoint for Railway healthchecks
- production-safe startup without the Flask dev server

### 1. Add services

- Create a Railway project
- Add your web service from this repo
- Add a MySQL service
- Add a Redis service

### 2. Set variables on the web service

Set at least:

```text
APP_CONFIG=ProductionConfig
JWT_SECRET_KEY=replace-this-with-a-real-secret
```

Then provide database access using one of these approaches:

- Preferred: map Railway MySQL variables into `DATABASE_URL`
- Supported automatically: `MYSQL_URL`, `MYSQL_PUBLIC_URL`, or `MYSQLHOST` / `MYSQLPORT` / `MYSQLUSER` / `MYSQLPASSWORD` / `MYSQLDATABASE`

For Redis, set one of:

```text
REDIS_URL=redis://...
```

Optional explicit overrides:

```text
CACHE_REDIS_URL=redis://...
RATELIMIT_STORAGE_URI=redis://...
```

### 3. First deploy

Push the repo and deploy. Railway will:

- install the Python dependencies from `requirements.txt`
- start the app with `gunicorn app:app`
- call `/health` for healthchecks

### 4. Optional schema bootstrap

If you want Railway to create tables on first boot without migrations, set:

```text
AUTO_CREATE_TABLES=true
```

This is acceptable for a first deploy or demo environment, but it is not a migration strategy.

## API Summary

### Auth

- `POST /auth/login`
- `POST /auth/refresh`

### Members

- `POST /members/`
- `GET /members/`
- `GET /members/<member_id>`
- `GET /members/me`
- `PUT /members/<member_id>`
- `DELETE /members/<member_id>`

### Books

- `POST /books/`
- `GET /books/`
- `GET /books/search?q=<term>`
- `GET /books/<book_id>`
- `PUT /books/<book_id>`
- `DELETE /books/<book_id>`

### Loans

- `POST /loans/`
- `GET /loans/`
- `GET /loans/me`
- `GET /loans/<loan_id>`
- `PUT /loans/<loan_id>`
- `DELETE /loans/<loan_id>`

## Auth Notes

- `POST /auth/login` returns `access_token` and `refresh_token`
- protected requests should send `Authorization: Bearer <access-token>`
- the frontend stores tokens in `localStorage`
- `POST /auth/refresh` accepts a refresh token and returns a new access token

## Rate Limiting

Configured in `app/extensions.py`.

- default global limit: `200 per day, 50 per hour`
- application limit: `1000 per hour`
- auth login limit: `5 per minute`
- auth refresh limit: `10 per minute`
- heavy read limit: `20 per minute`
- search limit: `10 per minute`

Limit breaches return JSON `429` responses.

## Caching

Configured in `app/extensions.py`.

- development and testing default to `SimpleCache`
- production defaults to `RedisCache`
- cached reads are invalidated after writes

## Production Notes

- Use `gunicorn`, not `python app.py`, in production
- Replace the default JWT secret before deploying
- Keep Redis available in production for shared rate limiting and cache storage
- Prefer migrations for schema changes instead of relying on `AUTO_CREATE_TABLES`
- Railway deploys on Linux, so Windows-only packages like `pywin32` should not be in production dependencies
