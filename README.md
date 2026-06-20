# Dazah Backend

原料药事业部工厂数字化基座后端服务。

## Tech Stack

- **Python 3.12+** with FastAPI
- **PostgreSQL 17** + **Redis**
- **SQLAlchemy 2.0** (async) + **Alembic** (migrations)
- **Pydantic v2** for validation
- **uv** for package management

## Quick Start

### Prerequisites

- Python >= 3.12
- PostgreSQL 17
- Redis
- [uv](https://docs.astral.sh/uv/)

### Setup

```bash
# 1. Install dependencies
uv sync

# 2. Install Playwright (required for regulatory tracker crawler)
playwright install chromium

# 3. Configure environment
cp .env.example .env
# Edit .env with your database and Redis credentials

# 4. Database migrations
alembic upgrade head

# 5. Seed initial data (regulatory tracker)
python scripts/seed_regulatory_tracker.py
python scripts/seed_regulatory_documents.py

# 6. Start the server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Access the API docs at http://localhost:8000/docs

## Architecture

Modular monolith with clear boundaries:

```
app/
├── core/              # Infrastructure (config, database, security, exceptions)
├── shared/            # Cross-module contracts (base models, module registry)
├── platform/          # Platform capabilities (audit, identity, integrations)
├── modules/           # Business modules
│   ├── production/    # 生产管理
│   ├── equipment/     # 设备管理
│   ├── safety/        # 安全管理
│   ├── energy/        # 能源管理
│   ├── quality/       # 质量管理
│   ├── hr/            # 人事管理
│   ├── registration/  # 注册管理
│   ├── research/      # 研发管理
│   └── ...
└── api/               # Global router
```

Each module maintains its own API routes, schemas, services, repositories, and models.

## Business Modules

| Module | Description |
|--------|-------------|
| **Production** | Batch management, process records, material balance |
| **Equipment** | Asset registry, maintenance, inspection, spare parts |
| **Safety** | Hazard identification, risk management, special operations |
| **Energy** | Device monitoring, alerts, collection logs |
| **Quality** | Deviations, CAPA, CPV (process validation) |
| **HR** | Employee profiles, onboarding, training, attendance |
| **Registration** | Dossier writing, regulatory tracking, supplementary replies |
| **Research** | Experiments, Bayesian optimization, ICH analysis |

## Development

```bash
# Run tests
uv run pytest

# Code quality
uv run ruff check .
uv run mypy app/

# Format code
uv run ruff format .
```

### Database Migrations

```bash
# Create migration (after modifying models)
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

**Important**: When adding a new schema, manually add `CREATE SCHEMA IF NOT EXISTS` at the start of `upgrade()` — Alembic won't generate it automatically.

## Docker Deployment

```bash
# Start database and Redis
docker compose --profile db up -d

# Run migrations
docker compose run --rm app uv run alembic upgrade head

# Seed data
docker compose run --rm app uv run python scripts/seed_regulatory_tracker.py
docker compose run --rm app uv run python scripts/seed_regulatory_documents.py

# Install Playwright in container
docker compose run --rm app uv run playwright install chromium

# Start application
docker compose --profile app up -d
```

## Environment Variables

Key variables in `.env`:

- `APP_DATABASE_URL` — PostgreSQL connection string
- `APP_REDIS_URL` — Redis connection string
- `SECRET_KEY` — JWT secret (change in production)
- `API_BASE_URL` — Backend URL for frontend server-side requests

See `.env.example` for the full list.

## Frontend Integration

The frontend (`dazah-frontend/`) is a Next.js application that connects to this backend:

- **Development**: Next.js proxy forwards `/api/v1/*` requests to backend
- **Production**: nginx reverse proxy handles routing
- **API path**: All endpoints under `/api/v1/<module>/<resource>`

## Health Check

```bash
curl http://localhost:8000/health
```
