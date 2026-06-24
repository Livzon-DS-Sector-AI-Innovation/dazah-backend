# dazah-backend AI 编程规范

## 项目原则

`dazah-backend` 是原料药事业部的工厂数字化基座后端，采用模块化单体架构，承载生产、设备、安全、环保、能源、仓储、采购、行政、人事、研发、注册、质量等业务模块。

目标是让各模块在统一平台能力下独立演进，并保留审计、身份扩展、外部系统集成能力。不要把项目改成微服务，也不要引入与当前需求无关的复杂架构。

技术栈：Python 3.12+、FastAPI、SQLAlchemy 2.0 async、PostgreSQL、Redis、Alembic、Pydantic v2、uv、pytest、ruff、mypy、MinIO。

涉及不确定的新 API 或库写法时，先查最新官方文档或 Context7，再实现。

## 目录边界

- `app/core/`：技术基础设施，例如配置、数据库、Redis、异常、统一响应、事件总线。
- `app/shared/`：跨平台和业务模块共享的轻量契约，例如 ORM 基类、模块注册表、通用 schema。
- `app/platform/`：工厂级平台能力，例如审计、身份、本地用户档案、外部系统集成。
- `app/modules/`：业务模块。每个模块维护自己的 API、Schema、Service、Repository、Model。
- `app/api/router.py`：全局 API 路由装配入口。
- `alembic/`：数据库迁移。

禁止把新业务代码放回旧式横向目录，例如 `app/models/`、`app/schemas/`、`app/integrations/`。模块清单以 `app/shared/module_registry.py` 和实际目录为准。

## 协作编辑边界

只能修改自己负责模块内的代码。除非需求明确要求并经过负责人确认，不要编辑项目架构、全局基础设施、平台能力或其他人负责的业务模块。

涉及跨模块改动时，优先通过目标模块的 `public_api.py`、模块注册表或既有扩展点完成协作；确实需要修改其他模块内部实现时，必须先说明影响范围、原因和验证方式，并尽量让对应负责人处理。

严禁借一次需求顺手重构不归自己负责的模块、移动目录、调整公共抽象或改变架构边界。对 `app/core/`、`app/shared/`、`app/platform/`、`app/api/router.py`、`alembic/` 等全局或平台级文件的编辑应保持最小化，并只限于当前需求不可避免的变更。

## 业务模块结构

详见 [examples/module-structure.md](examples/module-structure.md)。

## API 规范

路由统一挂在 `/api/v1` 下，常用形式：

```text
GET    /api/v1/{module}/
POST   /api/v1/{module}/{resource}
GET    /api/v1/{module}/{resource}
GET    /api/v1/{module}/{resource}/{id}
PUT    /api/v1/{module}/{resource}/{id}
DELETE /api/v1/{module}/{resource}/{id}
```

- 入参和出参使用本模块 `schemas.py`。
- 返回格式优先使用 `app/core/response.py`。
- 业务异常优先使用 `app/core/exceptions.py`。
- 删除业务数据默认软删除，例如 `is_deleted`；除非需求明确要求，不做物理删除。

## 数据库与迁移

数据库使用 PostgreSQL schema 做边界隔离：

- `identity`：本地轻量用户档案，后续关联飞书 SSO。
- `audit`：审计日志和操作追踪。
- 每个业务模块一个 schema，例如 `production`、`quality`、`equipment`。

ORM 和 migration 规则：

- 业务模型继承 `app/shared/base_model.py` 中的 `BaseModel`。
- 每张业务表必须有清晰的 `__tablename__` 和 `__table_args__ = {"schema": "<module_schema>"}`。
- 字段命名使用英文 `snake_case`。
- 唯一约束、外键、常用查询索引要显式声明。
- 修改 ORM 模型后必须新增 Alembic migration。
- 不要修改已经合并或执行过的历史 migration，除非用户明确要求。
- 新增 schema 时同步更新 `app/shared/module_registry.py` 和 migration。
- **autogenerate 不会自动生成 `CREATE SCHEMA` 语句**。每次新增 schema 或生成包含新 schema 建表语句的迁移时，必须在 `upgrade()` 开头手动添加 `op.execute("CREATE SCHEMA IF NOT EXISTS <schema_name>")`，否则空库部署会报错。

常用命令见 [examples/commands.md](examples/commands.md)。

多人协作迁移规范：

Alembic 的 revision ID 是随机哈希，多人同时创建 migration 会产生多个 head（分支），导致 `alembic upgrade head` 失败或生产环境 ORM 与数据库不一致。必须遵守以下流程：

**创建 migration 前的固定步骤（每次都要做）：**

```bash
git pull                                    # 1. 拉取最新代码
uv run alembic heads                        # 2. 检查 head 数量
uv run alembic merge heads -m "merge heads" # 3. 多个 head 时先合并
uv run alembic upgrade head                 # 4. 升级本地数据库
uv run alembic revision --autogenerate -m "xxx"  # 5. 再创建自己的 migration
```

**禁止事项：**

- 禁止提交包含 git 冲突标记（`<<<<<<<`）的 migration 文件，这会让整个 alembic 崩溃。
- 禁止手动写 revision ID（如 `20260615_0001`），使用 alembic 自动生成的随机哈希，避免 ID 重复。
- 禁止在生产环境出现多个 head。合并代码后、部署前，必须确认 `alembic heads` 只有一个。
- 禁止跳过 `alembic upgrade head` 直接创建 migration，否则 `down_revision` 会指向过时的节点。

**部署前检查清单：**

```bash
uv run alembic heads     # 必须只有一个 head
uv run alembic current   # 确认数据库版本
uv run alembic upgrade head  # 确保能顺利升级
```

如果 `autogenerate` 混入了其他模块的无关变更，手动清理 migration 文件，只保留自己模块的 DDL。


### 迁移工作流（重要）

当前状态：数据库已整合到单一 baseline 迁移 (`68024feea3d7`)，所有历史中间迁移已删除。

**创建新迁移的标准流程：**

```bash
# 1. 确保本地数据库是最新的
alembic upgrade head

# 2. 修改 SQLAlchemy 模型（在 app/modules/<module>/models.py）

# 3. 生成迁移文件
alembic revision --autogenerate -m "add_xxx_table"

# 4. 检查生成的迁移文件
# - 确认 upgrade() 和 downgrade() 都正确
# - 确认只包含你模块的变更
# - 如果有新 schema，确保 upgrade() 开头有 CREATE SCHEMA IF NOT EXISTS

# 5. 测试迁移
alembic upgrade head      # 升级
alembic downgrade -1      # 降级
alembic upgrade head      # 再升级

# 6. 提交前检查
alembic heads             # 必须只有一个 head
alembic current           # 确认数据库版本
```

**团队协作规则：**

- 创建迁移前必须 `git pull` 并运行 `alembic upgrade head`
- 如果有多个 head，先合并：`alembic merge heads -m "merge heads"`
- 不要修改已推送的迁移文件，如需变更，创建新的迁移
- 部署前必须确认 `alembic heads` 只有一个

**何时需要整合迁移（consolidate）：**

- 迁移文件过多（>20个）且难以追踪
- 迁移链出现严重冲突或断裂
- 重大版本发布后，清理历史

整合步骤：
```bash
# 1. 生成完整的 baseline 迁移
alembic revision -m "baseline"
# 手动编辑迁移文件，包含完整的 CREATE TABLE 语句

# 2. 删除所有旧的迁移文件（保留新的 baseline）

# 3. 更新数据库版本
psql -c "UPDATE alembic_version SET version_num = '<new_baseline_id>'"

# 4. 验证
alembic current
alembic heads
```
## 审计、身份与外部集成

- 新增、修改、删除、审批、导入、同步等关键业务操作，应考虑通过 `app/platform/audit/service.py` 记录审计信息。
- 需要当前用户时，通过 `app/platform/identity/deps.py` 的依赖注入获取，不要在业务模块里直接解析 header、cookie 或飞书 token。
- 飞书、ERP、LIMS 等外部系统统一放在 `app/platform/integrations/`，业务模块通过 integration service 或 adapter 调用，不直接散落 HTTP 请求。
- 外部调用要考虑超时、重试、幂等和失败记录。

## 编码风格

- 使用 Python 3.12 类型标注。
- Pydantic 使用 v2 写法。
- SQLAlchemy 使用 2.0 typed ORM：`Mapped[...]` 和 `mapped_column(...)`。
- 异步数据库访问使用 `AsyncSession`。
- 函数保持短小，业务逻辑放 `service.py`，查询放 `repository.py`。
- 不引入无必要的大型抽象。
- 不做与当前需求无关的重构。
- 不提交临时调试代码、`print` 或无用注释。
- 中文业务名可以写在 API `summary`、`description` 和文档中；代码标识符使用英文。
- **SQLAlchemy async 铁律：禁止 `db.refresh()`、禁止直接赋值未加载的 relationship。写操作后统一用 `select+selectinload` eager re-fetch 返回对象。**（不遵守会出 MissingGreenlet）
  - **为什么 INSERT 后 `flush()` 就够了？** PostgreSQL 方言对 INSERT 使用 `RETURNING` 子句，SQLAlchemy 会自动回填 `id`、`created_at`、`updated_at` 等 server default 值到内存对象。所以 `create` 类操作可以 flush 后直接返回，无需 re-fetch。
  - **为什么 UPDATE 后必须 re-fetch？** `flush()` 对 UPDATE 不使用 RETURNING，`onupdate` 的 `updated_at` 不会回填到内存对象。若后续 Pydantic `model_validate` 或上层代码访问该属性，SQLAlchemy 会触发懒加载——此时若已脱离 async session 上下文（如 FastAPI 响应序列化阶段），即报 MissingGreenlet。
  - **简单记忆：INSERT → flush 返回即可；UPDATE/DELETE → flush 后必须 select re-fetch。**
- 设计数据库表时，不要用外键约束。
- 如果新增/修改了本地env文件，需要同步修改到env example中。

## AI 工作流程

1. 先阅读 `AGENTS.md` 和必要的架构/代码文件，判断需求属于哪个模块或平台能力。
2. 明确自己负责的模块边界，默认只修改该模块目录内的代码；不要编辑其他人负责的模块或项目架构。
3. 只有当前需求确实需要平台能力时，才最小范围修改 `core`、`shared` 或 `platform`，并说明原因。
4. 字段、流程、权限规则不明确时，先按现有架构做保守实现；不能合理推断时再提出待确认点。
5. 涉及数据库变更时，同步 ORM、migration、模块注册和测试。
6. 完成后说明修改文件、验证结果、跨模块或架构影响，以及未完成事项。

## API 路由架构

前端通过统一的反向代理访问后端 API，开发和生产环境配置完全一致。

### 路由转发机制

- **开发环境**：浏览器 → Next.js (3000) → `src/proxy.ts` → 后端 (8000)
- **生产环境**：浏览器 → nginx → Next.js (3000) 或 后端 (8000)
- **前端服务器端**：直接通过 `API_BASE_URL` 环境变量访问后端（Docker内部网络）

### API 路径规范

- 所有 API 路径以 `/api/v1/` 开头
- 按模块组织：`/api/v1/<模块>/<资源>`
- 示例：`/api/v1/production/batches`、`/api/v1/quality/cpv/products`

### 环境变量

- `API_BASE_URL`：前端服务器端访问后端的地址（Docker 内部网络）
- 前端客户端代码使用相对路径 `/api/v1/...`，无需关心后端真实地址
- 开发环境通过 Next.js proxy 自动转发
- 生产环境由 nginx 反向代理处理

### 注意事项

- 后端服务运行在 Docker 网络内部，地址为 `http://dazah-backend-app-1:8000`
- 前端通过 `API_BASE_URL` 环境变量访问后端（服务器端代码）
- 前端客户端通过相对路径 `/api/v1/...` 访问（由 proxy/nginx 转发）
