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

## 飞书集成边界

飞书相关开发必须严格区分“平台通用能力”和“模块业务集成”。不要把某个业务模块的飞书配置、表结构、同步逻辑提升成全局统一配置，也不要让一个业务模块直接引用另一个业务模块的飞书实现。

### 平台飞书通用能力

`app/platform/integrations/feishu/` 只承载跨模块可复用的飞书基础能力，例如：

- 飞书 HTTP/API 基础客户端、事件接入、消息发送等平台能力。
- 多维表格 URL、`app_token`、`table_id`、`view_id` 的解析与标准化。
- 基于调用方显式传入的 `app_id`、`app_secret`、`app_token`、`table_id` 做连通性测试。

飞书配置解析层位于 `app/platform/integrations/feishu/utils.py`。它是无状态工具层，只做解析和即时请求，不保存、不读取、不决定任何模块的飞书配置来源。新开发中需要解析完整多维表格链接、`app_token:` 文本、`table=tbl...` 或测试多维表格表访问时，优先复用这里的函数。

平台通用能力禁止：

- 禁止新增统一飞书配置表来保存各业务模块的 App ID、App Secret、token、app_token 或 table_id。
- 禁止在解析层读取仓储、安全、设备、HR、产品等业务模块配置。
- 禁止在解析层读取 `get_settings()` 来替业务模块决定凭证来源。
- 禁止在解析层持久化或缓存 token；是否缓存、如何刷新由各业务模块自己的服务决定。
- 禁止从 `app/platform/integrations/feishu/` 反向导入 `app.modules.*`。

### 模块飞书业务集成

每个业务模块必须拥有自己的飞书配置来源和业务服务：

- 仓储模块使用自己的 `warehouse.feishu_configs`、仓储配置页面和仓储服务。
- 安全模块使用现有 `SAFETY_FEISHU_*` 环境配置和 `app/modules/safety/feishu/` 业务代码。
- 设备、HR、产品等模块沿用各自模块内的配置来源和业务实现。

模块调用平台飞书工具时，必须先在本模块内读取、解密、校验自己的配置，再把显式参数传给平台 helper。平台 helper 不应知道这些参数来自哪个模块、哪张业务表或哪个页面。

模块边界禁止：

- 禁止任一业务模块直接复用另一个业务模块的飞书配置表、service、handler 或同步逻辑。
- 飞书事件订阅、长连接、卡片审批、多维表格同步等业务流程必须放在所属模块目录下；平台层最多负责接入飞书事件并发布平台内部事件或提供通用客户端。

## 协作编辑边界

只能修改自己负责模块内的代码。除非需求明确要求并经过负责人确认，不要编辑项目架构、全局基础设施、平台能力或其他人负责的业务模块。

涉及跨模块改动时，优先通过目标模块的 `public_api.py`、模块注册表或既有扩展点完成协作；确实需要修改其他模块内部实现时，必须先说明影响范围、原因和验证方式，并尽量让对应负责人处理。

严禁借一次需求顺手重构不归自己负责的模块、移动目录、调整公共抽象或改变架构边界。对 `app/core/`、`app/shared/`、`app/platform/`、`app/api/router.py`、`alembic/` 等全局或平台级文件的编辑应保持最小化，并只限于当前需求不可避免的变更。

## 业务模块结构

详见 [examples/module-structure.md](examples/module-structure.md)。

## API 规范

路由统一挂在 `/api/v1` 下，按模块组织：`/api/v1/<模块>/<资源>`。

常用形式：

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

### 前端访问方式

前端通过统一的反向代理访问后端 API，开发和生产环境配置完全一致：

- **开发环境**：浏览器 → Next.js (3000) → `src/proxy.ts` → 后端 (8000)
- **生产环境**：浏览器 → nginx → Next.js (3000) 或 后端 (8000)
- **前端服务器端**：直接通过 `API_BASE_URL` 环境变量访问后端（Docker 内部网络，地址为 `http://dazah-backend-app-1:8000`）

## Livzon Agent 工具开发规范

Livzon Agent 不能直接操作数据库，也不能自由调用任意后端 API。所有暴露给 Agent 的业务能力必须通过 `app.modules.agent.tools.@agent_tool` 注册，并由 `ToolRegistry` 和 `ToolExecutor` 统一执行。

### 核心边界

- Agent 只能调用已注册到 `ToolRegistry` 的工具，未注册 operation 一律拒绝。
- Hermes-Lite 只能通过 `/api/v1/agent/tools/execute` 调用后端工具网关，不得绕过后端访问业务接口。
- 工具 handler 只能调用本模块 Service 或明确公开的 `public_api.py`，禁止直接操作 ORM model、repository 私有实现或拼 SQL。
- 禁止业务模块工具直接复用另一个业务模块的内部 service、handler、repository 或配置来源；跨模块协作优先通过目标模块 `public_api.py`。
- 权限、参数校验、确认流程和审计由 `ToolExecutor` 统一处理，业务工具不要自行另造一套 Agent 权限/确认/审计链路。

### 新增工具标准流程

1. 在所属业务模块 Service 中实现业务逻辑，保持业务规则仍在模块内。
2. 在 `app/modules/<module>/agent_tools.py` 中定义 Pydantic v2 InputSchema。
3. 使用 `@agent_tool(...)` 注册工具，声明 `name`、`summary`、`input_model`、`write`、`risk_level`、`workflow_allowed`、`human_decision_required` 等元数据。
4. handler 接收 `ToolContext` 和已校验的 InputSchema，只做薄封装和结果序列化。
5. 在 `app/modules/agent/tool_registration.py` 导入该模块 `agent_tools.py`，确保 FastAPI 启动时触发注册。
6. 为注册、参数校验、权限、确认、高风险拒绝和核心业务调用补测试。
7. 若新增或修改 Agent API，运行 `uv run python scripts/export_openapi.py` 更新 `openapi.json`。
8. 前端同步运行 `pnpm generate:api` 更新生成类型。
9. 如果 Hermes-Lite 仍使用静态工具 schema，同步更新 `Hermes-Lite/tools/dazah_platform.py` 的 `ALLOWED_OPERATIONS` 和相关 README/提示词。

示例：

```python
from pydantic import BaseModel, Field

from app.modules.agent.tools import ToolContext, agent_tool


class QualityInspectionListInput(BaseModel):
    status: str | None = None
    keyword: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


@agent_tool(
    name="quality.list_inspections",
    summary="查询质量检查记录",
    input_model=QualityInspectionListInput,
    write=False,
    risk_level="medium",
    workflow_allowed=True,
    method="GET",
    path="/quality/inspections",
)
async def list_quality_inspections(
    context: ToolContext,
    data: QualityInspectionListInput,
) -> dict:
    service = QualityService(context.db)
    result = await service.list_inspections(
        status=data.status,
        keyword=data.keyword,
        page=data.page,
        page_size=data.page_size,
    )
    return result.model_dump(mode="json")
```

### 工具命名与元数据

- 工具名使用 `<module>.<verb>_<resource>`，例如 `warehouse.list_raw_materials`、`procurement.create_purchase_request`。
- 查询类工具优先使用 `list_*`、`get_*`。
- 写入类工具优先使用 `create_*`、`update_*`、`set_*`、`submit_*`、`sync_*`、`run_*`。
- `summary` 使用清晰中文，便于 Agent 选择工具。
- `input_model` 必须是 Pydantic v2 模型，不要让工具 handler 自己解析松散 dict。
- `method` / `path` 仅作为兼容和展示元数据，不代表 Agent 可以直接调用该 HTTP API。

### 风险与确认规则

- `write=False` 的查询工具可直接执行。
- `write=True` 的工具默认只生成 `agent_confirmations` 确认项，用户确认后才执行。
- `risk_level` 可选 `low`、`medium`、`high`。
- 审批、驳回、批准、重启关键连接等需要人工责任判断的操作，必须设置 `human_decision_required=True`，不得由 Agent 代执行。
- `human_decision_required=True` 的工具必须同时设置 `workflow_allowed=False`。
- 工作流只允许包含 `workflow_allowed=True` 且 `human_decision_required=False` 的业务工具。

### 审计与可追踪性

- 每次工具调用必须经过 `ToolExecutor`，并写入 `core.agent_tool_calls`。
- 工具执行、确认执行和策略拒绝必须写入 `audit.logs`。
- 审计中不得记录明文 secret、token、password、key 等敏感字段。
- 工具返回大对象时应返回业务摘要或分页结果，避免把过大响应写入审计。

### 禁止事项

- 禁止在 Hermes-Lite 中新增绕过 Dazah 后端的业务 HTTP 调用。
- 禁止 Agent 工具直接连接 PostgreSQL、Redis、飞书业务表或第三方业务系统。
- 禁止工具 handler 直接 `db.execute()` 拼业务 SQL，除非这是本模块 Service 已定义并审查过的底层实现。
- 禁止把审批、驳回、批准等责任判断伪装成普通写操作。
- 禁止新增工具后不补 `tool_registration.py`、测试和 OpenAPI 同步。

## 数据库与迁移

数据库使用 PostgreSQL schema 做边界隔离：

- `identity`：本地轻量用户档案，后续关联飞书 SSO。
- `audit`：审计日志和操作追踪。
- 每个业务模块一个 schema，例如 `production`、`quality`、`equipment`。
- `core`：平台级配置（如 LLM 配置）。

### ORM 规则

- 业务模型继承 `app/shared/base_model.py` 中的 `BaseModel`。
- 每张业务表必须有清晰的 `__tablename__` 和 `__table_args__ = {"schema": "<module_schema>"}`。
- 字段命名使用英文 `snake_case`。
- 唯一约束、外键、常用查询索引要显式声明。
- 不要修改已经合并或执行过的历史 migration，除非用户明确要求。
- 新增 schema 时同步更新 `app/shared/module_registry.py` 和 migration。
- **autogenerate 不会自动生成 `CREATE SCHEMA` 语句**。每次新增 schema 或生成包含新 schema 建表语句的迁移时，必须在 `upgrade()` 开头手动添加 `op.execute("CREATE SCHEMA IF NOT EXISTS <schema_name>")`，否则空库部署会报错。
- 设计数据库表时，不要用外键约束。
- 如果新增/修改了本地 env 文件，需要同步修改到 env example 中。

常用命令见 [examples/commands.md](examples/commands.md)。

### ⚠️ 迁移铁律（CI 会自动检查，违反会导致 PR 无法合并）

**1. 模型变更必须伴随迁移**
- 新增、删除、重命名 SQLAlchemy 模型时，**必须同时创建并审查 Alembic migration**
- 禁止只改模型不写迁移，禁止手动执行 SQL 改表结构
- CI 会运行 `alembic check`，检测到 drift 会阻止合并

**2. 禁止盲目执行 autogenerate**
- **永远不要**直接 `alembic revision --autogenerate` 后立即 `upgrade`
- 必须先审查生成的迁移文件，确认只包含本次需求的变更
- 如果 autogenerate 包含无关变更（其他模块的表、删除表等），**立即停止**

**3. 只创建针对性迁移**
- 如果 autogenerate 检测到大量无关变更，说明数据库与模型已不同步
- **不要**尝试用一个大迁移修复所有问题
- **应该**手动编写只包含当前需求表的迁移（使用 `CREATE TABLE IF NOT EXISTS`）
- 或者先解决根本原因（恢复 baseline、清理孤儿表等）

**违反后果示例：**
- 删除模型不写迁移 → 数据库残留孤儿表 → autogenerate 试图 DROP 其他表
- 盲目执行 autogenerate → 误删生产数据（DROP TABLE）
- 手动改表不写迁移 → 其他开发者环境不一致 → 部署失败

### 多人协作迁移规范

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

- 禁止提交包含 git 冲突标记（`<<<<<<<`）的 migration 文件
- 禁止手动写 revision ID（如 `20260615_0001`），使用 alembic 自动生成的随机哈希
- 禁止在生产环境出现多个 head。合并代码后、部署前，必须确认 `alembic heads` 只有一个
- 禁止跳过 `alembic upgrade head` 直接创建 migration，否则 `down_revision` 会指向过时的节点
- 禁止在迁移文件中包含未经确认的 DROP TABLE 操作

**部署前检查清单：**

```bash
uv run alembic heads          # 必须只有一个 head
uv run alembic current        # 确认数据库版本
uv run alembic upgrade head   # 确保能顺利升级
uv run alembic check          # 确认无 drift
```

如果 `autogenerate` 混入了其他模块的无关变更，手动清理 migration 文件，只保留自己模块的 DDL。

### 迁移工作流

当前状态：数据库已整合到单一 baseline 迁移 (`bf9ec662358f`，2026-06-25 重建)，所有历史中间迁移已删除。

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
# - 确认没有 DROP TABLE（除非你明确要删除）
# - 如果包含其他模块的变更，手动删除那些部分

# 5. 应用迁移
alembic upgrade head

# 6. 提交代码（模型 + 迁移文件一起提交）
git add app/modules/<module>/models.py alembic/versions/<hash>_add_xxx_table.py
git commit -m "feat(<module>): add xxx table with migration"
```

**关键点：**
- 模型文件和迁移文件必须在同一个 commit 中
- CI 会检查 `alembic check`，如果有 drift 会阻止合并
- 迁移文件命名由 alembic 自动生成，不要手动修改

## 编码风格

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

## OpenAPI 规范与前端同步

后端 API 是前端的唯一数据源。每次修改 API 后，必须更新 OpenAPI spec 并提交，确保前端类型与后端保持同步。

**工作流程：**

1. 修改 API 后运行 `uv run python scripts/export_openapi.py` 更新 `openapi.json`
2. 将 `openapi.json` 一起提交到 git
3. 前端开发者运行 `pnpm generate:api` 重新生成类型

**CI 检查：** GitHub Actions 会自动检查 `openapi.json` 是否与后端代码同步，检测到 drift 会阻止合并。

**注意：** 禁止手动编辑 `openapi.json`，它由 FastAPI 自动生成。每次 API 变更（新增/修改/删除端点、修改参数或响应结构）都必须重新生成 spec。

前端使用 `openapi-typescript` 从 `openapi.json` 生成 TypeScript 类型定义（`src/types/generated/schema.ts`），所有 API 相关的类型必须从生成文件导入，禁止手写 API 类型。

## LLM 调用规范

所有需要调用 LLM 的业务模块必须使用 `app.core.llm` 提供的统一客户端，禁止直接使用 `AIService` 或其他自定义方式。

### 正确用法

```python
from app.core.llm import llm_client

# 文本对话（返回字符串）
response = await llm_client.chat(
    messages=[
        {"role": "system", "content": "你是一个助手"},
        {"role": "user", "content": "你好"}
    ],
    temperature=0.1,
    max_tokens=4096
)

# 文本对话（返回 JSON dict）
result = await llm_client.chat_json(
    messages=[
        {"role": "system", "content": "你是一个分析助手"},
        {"role": "user", "content": "分析这段文本..."}
    ],
    expected_keys=["conclusion", "reasoning"]
)

# 视觉模型（图片分析）
response = await llm_client.chat_vision(
    text_prompt="分析这张图片",
    image_urls=["https://example.com/image.jpg"]
)

# 视觉模型（返回 JSON）
result = await llm_client.chat_vision_json(
    text_prompt="识别图片中的缺陷",
    image_urls=[base64_data_uri],
    expected_keys=["defect_type", "severity"]
)

# 流式输出
async for chunk in llm_client.stream_chat(messages=messages):
    if chunk["type"] == "content":
        yield chunk["text"]
```

### 配置来源

`llm_client` 按以下优先级读取配置：

1. **数据库配置**（`core.llm_configs` 表）：管理员通过后台界面配置的模型，支持加密存储 API key
2. **环境变量**（仅开发环境）：`LLM_API_KEY`、`LLM_BASE_URL`、`LLM_MODEL`

生产环境必须在数据库中配置 LLM，否则会抛出 `LLMConfigError`。

### 禁止用法

以下写法是错误的，会导致运行时错误或安全问题：

```python
# ❌ 错误：直接使用 AIService
from app.platform.integrations.ai.client import AIService
ai = AIService(api_key="...", base_url="...", model="...")

# ❌ 错误：使用 get_ai_service()（读取空的环境变量）
from app.platform.integrations.ai import get_ai_service
ai = get_ai_service()

# ❌ 错误：使用 create_ai_service()（硬编码的 API key）
from app.modules.safety.service.config import create_ai_service
ai = create_ai_service("text")

# ❌ 错误：手动读取环境变量构造客户端
api_key = os.getenv("AI_API_KEY", "")
ai = AIService(api_key=api_key, ...)
```

### 异常处理

```python
from app.core.llm import llm_client, LLMOutputError, LLMProviderError, LLMRateLimitError

try:
    result = await llm_client.chat_json(messages=messages)
except LLMOutputError:
    # LLM 返回的内容不是有效的 JSON，或缺少必要的字段
    logger.error("LLM 输出格式错误")
except LLMProviderError:
    # LLM API 返回错误（如 401、500）
    logger.error("LLM 服务调用失败")
except LLMRateLimitError:
    # 触发速率限制
    logger.warning("LLM 速率限制")
```

### 迁移指南

如果现有代码使用了错误的调用方式，按以下步骤迁移：

1. 替换导入：`from app.core.llm import llm_client`
2. 删除所有 `AIService` 实例化代码
3. 删除所有 `_get_ai_service()` 或类似工厂方法
4. 将 `ai.chat()` 替换为 `llm_client.chat()` 或 `llm_client.chat_json()`
5. 将 `ai.chat_vision()` 替换为 `llm_client.chat_vision()` 或 `llm_client.chat_vision_json()`
6. 删除所有 `await ai.close()` 调用（`llm_client` 自动管理连接）
7. 更新异常处理：`AIOutputError` → `LLMOutputError`
