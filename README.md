# Dazah Backend API

FastAPI-based backend service for the Dazah platform.

## Prerequisites

- Docker & Docker Compose
- Python 3.12+ (for local development)

## Quick Start (Docker)

```bash
# Copy environment file
cp .env.example .env

# Start all services (API + PostgreSQL + Redis)
docker compose --profile app up -d

# View logs
docker compose --profile app logs -f app
```

Services will be available at:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

## Local Development

```bash
# Install dependencies
uv sync

# Run migrations
uv run alembic upgrade head

# Start dev server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Environment Variables

Key variables in `.env`:

- `APP_NAME`: Application name (default: dazah-backend)
- `APP_ENV`: Environment (development/production)
- `SECRET_KEY`: JWT secret (change in production!)
- `APP_DATABASE_URL`: PostgreSQL connection string
- `APP_REDIS_URL`: Redis connection string
- `POSTGRES_USER/PASSWORD/DB`: Database credentials

## Database Migrations

```bash
# Create new migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback one version
uv run alembic downgrade -1
```

## Production Deployment

```bash
# Build production image
docker build -t dazah-backend:latest .

# Run with production environment
docker compose --profile app up -d
```

Important: Set `SECRET_KEY` and database credentials in `.env` before deploying to production.

## Health Check

```bash
curl http://localhost:8000/health
```

## Stop Services

```bash
# Stop all services
docker compose --profile app down

# Stop and remove volumes (deletes data)
docker compose --profile app down -v
```
