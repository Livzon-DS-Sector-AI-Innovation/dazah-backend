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
