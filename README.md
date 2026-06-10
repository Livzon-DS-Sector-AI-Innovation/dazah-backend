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

### 5. 启动服务

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后访问：
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

## Docker 部署

```bash
# 启动数据库和 Redis
docker compose --profile db up -d

# 运行迁移
docker compose run --rm app uv run alembic upgrade head

# 启动应用
docker compose --profile app up -d
```

## 法规追踪模块

### 首次部署 — 初始化历史数据

服务启动后，调用初始化同步接口抓取 CDE 全量历史数据：

```bash
curl -X POST http://localhost:8000/api/v1/regulatory-tracker/sync-jobs/backfill
```

### 手动同步

```bash
curl -X POST http://localhost:8000/api/v1/regulatory-tracker/sync-jobs/manual-sync
```

### 查看同步日志

```bash
curl http://localhost:8000/api/v1/regulatory-tracker/sync-jobs
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
│   │   └── tasks/            # 后台任务
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
