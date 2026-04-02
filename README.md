# SafeCorridor Backend

FastAPI service for airport status, route patterns, and advisories.

## Local Run

1. Copy env:
   - `cp .env.example .env`
2. Install:
   - `python3 -m venv venv`
   - `source venv/bin/activate`
   - `pip install -r requirements.txt`
3. Seed data:
   - `python -m app.seed`
4. Run API:
   - `uvicorn app.main:app --reload --port 8000`

## Required Environment Variables

- `DATABASE_URL`  
  Example for PostgreSQL: `postgresql+psycopg2://user:password@host:5432/dbname`
- `CORS_ALLOWED_ORIGINS`  
  Comma-separated frontend origins.
- `APP_ENV`  
  Use `production` in deployed environments.
- `ADMIN_TOKEN`  
  Required for admin endpoints in production (`X-Admin-Token` header).
- `ENABLE_ADMIN_SEED`  
  Keep `false` by default in production.

## Deploy Targets

- Fly.io: `fly.toml` + `Dockerfile`
- Railway: `railway.toml` + `Dockerfile`

### No-GCP Setup

The current code does not require Google Cloud at runtime. The browser handles voice input/output locally, and the backend only needs a reachable HTTP deployment target.

For a no-card path:

- Run the backend locally or deploy it to a free host
- Keep the frontend on local Next.js or any static/Node-friendly host
