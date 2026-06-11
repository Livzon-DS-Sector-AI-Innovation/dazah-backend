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
# Dazah Backend

原料药事业部工厂系统后端服务。

## 环境要求

- Python >= 3.12
- PostgreSQL 17
- Redis
- [uv](https://docs.astral.sh/uv/) (Python 包管理器)

## 快速开始

### 1. 安装依赖

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
### 2. 安装 Playwright 浏览器（法规追踪爬虫需要）

```bash
playwright install chromium
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，确认 DATABASE_URL 和 REDIS_URL 正确
```

### 4. 数据库迁移

```bash
alembic upgrade head
```

### 5. 初始化种子数据

```bash
# 初始化法规追踪数据源和栏目
python scripts/seed_regulatory_tracker.py

# 导入初始法规数据（640条）
python scripts/seed_regulatory_documents.py
```

### 6. 启动后端服务

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
服务启动后访问：
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

### 7. 启动前端服务

前端项目位于 `dazah-frontend/` 目录。

```bash
cd ../dazah-frontend
pnpm install
pnpm dev --port 3000
```

前端页面访问：http://localhost:3000
- 法规跟踪页面：http://localhost:3000/registration/regulation

## 法规追踪模块

### 自动同步

服务启动后，Scheduler 会自动按 `DAILY_SYNC_CRON`（默认每天凌晨 02:00）执行同步任务，抓取 CDE 国内药品技术指导原则前 1-3 页的新增数据。

- 新增数据写入 `regulatory_documents`，标记 `is_new=true`
- 已存在数据仅更新 `last_checked_at`
- 同步日志写入 `sync_jobs` 和 `sync_job_pages`
- 同步失败不影响前端已有数据展示

### 查看同步日志

```bash
curl http://localhost:8000/api/v1/regulatory-tracker/sync-jobs
```

### 配置项

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `CRAWLER_HEADLESS` | 爬虫是否无头模式 | `true` |
| `CDE_GUIDELINE_URL` | CDE 指导原则列表页 URL | CDE 官方地址 |
| `DAILY_SYNC_CRON` | 每日同步 cron 表达式 | `0 2 * * *` |

## Docker 部署

> TODO: 本阶段 Docker 部署尚未完全验证，以下为参考流程。

```bash
# 启动数据库和 Redis
docker compose --profile db up -d

# 运行迁移
docker compose run --rm app uv run alembic upgrade head

# 初始化种子数据
docker compose run --rm app uv run python scripts/seed_regulatory_tracker.py
docker compose run --rm app uv run python scripts/seed_regulatory_documents.py

# 安装 Playwright 浏览器（容器内）
docker compose run --rm app uv run playwright install chromium

# 启动应用
docker compose --profile app up -d
```

## 项目结构

```
app/
├── api/              # 路由注册
├── core/             # 配置、数据库、安全
├── modules/          # 业务模块
│   ├── regulatory_tracker/   # 法规追踪
│   │   ├── api/              # API 路由
│   │   ├── crawler/          # 爬虫适配器
│   │   ├── models/           # ORM 模型
│   │   ├── schemas/          # Pydantic 模型
│   │   ├── services/         # 业务逻辑
│   │   └── tasks/            # 后台任务 (scheduler)
│   ├── quality/              # 质量管理 (CPV)
│   ├── registration/         # 注册管理
│   └── ...
├── platform/         # 平台级功能
└── shared/           # 公共基础类
```

## 开发

```bash
# 运行测试
uv run pytest

# 代码检查
uv run ruff check .

# 类型检查
uv run mypy app/
```
