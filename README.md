# Dazah Backend API

FastAPI-based backend service for the Dazah platform.

## Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- Docker & Docker Compose (for containerized deployment)

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

### 1. Clone the repository

```bash
git clone <repository-url>
cd dazah-backend
```

### 2. Install dependencies

```bash
uv sync
```

This will:
- Create `.venv` virtual environment
- Install all dependencies from `pyproject.toml`

### 3. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 4. Run database migrations

```bash
uv run alembic upgrade head
```

### 5. Start the server

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

Key variables in `.env`:

- `APP_NAME`: Application name (default: dazah-backend)
- `APP_ENV`: Environment (development/production)
- `SECRET_KEY`: JWT secret (change in production!)
- `APP_DATABASE_URL`: PostgreSQL connection string
- `APP_REDIS_URL`: Redis connection string
- `POSTGRES_USER/PASSWORD/DB`: Database credentials

## Key Features

### CPV Module (Continuous Process Validation)

- Product management (CRUD operations)
- CPP/CQA batch data import from Excel
- Data preview before import (supports create/update/overwrite modes)
- Batch data export to Excel
- Statistical analysis and trend visualization

#### Testing Excel Import Preview

```bash
curl -X POST "http://localhost:8000/api/v1/quality/cpv/import/preview?product_id=<product-id>&data_type=CPP&import_mode=create" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test.xlsx"
```

## Project Structure

```
.
├── app/
│   ├── api/              # API routes and dependencies
│   ├── core/             # Core configuration and utilities
│   ├── modules/          # Business logic modules
│   │   └── quality/      # Quality management (CPV)
│   │       ├── api/      # API endpoints
│   │       ├── service/  # Business logic
│   │       └── models/   # Database models
│   └── platform/         # Cross-cutting concerns
├── alembic/              # Database migrations
├── tests/                # Test suite
├── pyproject.toml        # Project dependencies
└── uv.lock              # Dependency lock file
```

## Database Migrations

```bash
# Create new migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback one version
uv run alembic downgrade -1
```

## Testing

```bash
uv run pytest
```

## Code Quality

```bash
# Run linter
uv run ruff check .

# Run type checker
uv run mypy .

# Format code
uv run ruff format .
```

## Dependencies

Key dependencies:
- **FastAPI**: Web framework
- **SQLAlchemy**: ORM with async support
- **Alembic**: Database migrations
- **openpyxl**: Excel file processing
- **psycopg / pg8000**: PostgreSQL drivers
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server

For a complete list, see `pyproject.toml`.

### Adding New Dependencies

```bash
uv add <package-name>
uv add --dev <package-name>
uv remove <package-name>
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
