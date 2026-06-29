# dazah-backend AI 编程规范

本文档定义 AI 编码助手必须遵守的规则。违反这些规则会导致代码被拒绝。

## 架构原则

本项目采用**模块化单体架构**，不是微服务。不要引入微服务、消息队列或其他复杂架构。

技术栈：Python 3.12+、FastAPI、SQLAlchemy 2.0 async、PostgreSQL 17、Redis、Alembic、Pydantic v2、uv、pytest、ruff、mypy、MinIO。

遇到不确定的 API 或库用法时，先查官方文档或 Context7，再实现。

## 目录结构

```
app/
├── core/              # 基础设施：配置、数据库、Redis、异常、响应、事件总线
├── shared/            # 跨模块契约：ORM 基类、模块注册表、通用 schema
├── platform/          # 平台能力：审计、身份、用户档案、外部集成
├── modules/           # 业务模块（每个模块独立维护 API、Schema、Service、Repository、Model）
└── api/router.py      # 全局路由装配
```

**禁止**：在 `app/models/`、`app/schemas/`、`app/integrations/` 等旧式横向目录中放置新业务代码。

## 模块所有权

每个业务模块由一个人负责。你只能修改自己负责的模块目录（`app/modules/<module>/`）。

**全局模块**（`app/core/`、`app/shared/`、`app/platform/`、`app/api/router.py`、`alembic/`）由架构负责人维护。其他模块只通过公共 API 调用它们。

**跨模块协作**：通过目标模块的 `public_api.py` 或模块注册表完成。如果必须修改其他模块内部实现，先说明影响范围、原因和验证方式，并让对应负责人处理。

**禁止**：借需求重构其他模块、移动目录、调整公共抽象或改变架构边界。

**环境变量**：按模块前缀组织（如 `SAFETY_AI_TEXT_MODEL`、`ENERGY_AUTO_COLLECT_ENABLED`）。

**全局层 vs 模块层**：全局层（如 `app/core/llm/`）只提供通用基础设施 API。业务功能代码（prompt、业务逻辑、错误处理）必须在模块内部，不要放到全局层。

## API 规范

所有路由挂在 `/api/v1` 下，按模块组织：`/api/v1/<module>/<resource>`。

标准形式：
```
GET    /api/v1/{module}/
POST   /api/v1/{module}/{resource}
GET    /api/v1/{module}/{resource}
GET    /api/v1/{module}/{resource}/{id}
PUT    /api/v1/{module}/{resource}/{id}
DELETE /api/v1/{module}/{resource}/{id}
```

**必须**：
- 入参和出参使用本模块 `schemas.py`
- 返回格式使用 `app/core/response.py`
- 业务异常使用 `app/core/exceptions.py`
- 删除业务数据默认软删除（`is_deleted`），不做物理删除（除非需求明确要求）

**前端访问方式**：
- 开发环境：浏览器 → Next.js (3000) → `src/proxy.ts` → 后端 (8000)
- 生产环境：浏览器 → nginx → Next.js (3000) 或后端 (8000)
- 前端服务器端：通过 `API_BASE_URL` 环境变量访问后端（Docker 内部网络，地址为 `http://dazah-backend-app-1:8000`）

## 数据库规范

使用 PostgreSQL schema 做模块隔离：
- `identity`：本地用户档案（后续关联飞书 SSO）
- `audit`：审计日志和操作追踪
- `core`：平台级配置（如 LLM 配置）
- 每个业务模块一个 schema（如 `production`、`quality`、`equipment`）

### ORM 规则

**必须**：
- 业务模型继承 `app/shared/base_model.py` 中的 `BaseModel`
- 每张表必须有 `__tablename__` 和 `__table_args__ = {"schema": "<module_schema>"}`
- 字段命名使用英文 `snake_case`
- 显式声明唯一约束、索引
- 新增 schema 时同步更新 `app/shared/module_registry.py`
- 新增/修改 env 文件时同步修改 env example

**外键约束规范**：
- 允许外键约束（包括跨模块），但必须避免级联删除（CASCADE DELETE）跨模块使用
- 跨模块关系必须明确记录在设计文档中
- 模块边界是组织结构，不是数据库约束边界
- 禁止循环外键依赖
- 对高风险删除操作必须使用软删除或应用层控制

**禁止**：
- 修改已合并或执行过的历史 migration（除非用户明确要求）

### 迁移规范

**命名规范**：`{revision_id}_{module}_{description}.py`

示例：
- `abc123_safety_add_hazard_table.py`
- `def456_equipment_add_inspection_route.py`

**单模块原则**：一个迁移文件只能修改一个模块的 schema。这样多人并行开发时合并冲突最小。

CI 会自动检查（`scripts/check_migration_scope.py`），违反会导致 PR 无法合并。

如果 `alembic revision --autogenerate` 生成了多个模块的变更：
1. 删除该迁移文件
2. 使用 `--include-object` 过滤，或手动编辑移除其他模块的变更

**CREATE SCHEMA**：Alembic 配置了自动钩子，会为新的 schema 自动生成 `CREATE SCHEMA IF NOT EXISTS`。无需手动添加。

**检查命令**：
```bash
python scripts/check_migration_scope.py alembic/versions/abc123_safety_add_table.py
```

## LLM 调用规范

**唯一正确的用法**：
```python
from app.core.llm import llm_client

# 文本对话
result = await llm_client.chat(messages=[...])

# 结构化输出（返回 dict）
parsed = await llm_client.chat_json(
    messages=[{"role": "user", "content": "分析这段文本"}],
    expected_keys=["summary", "keywords"]
)

# 视觉模型（图片分析）
result = await llm_client.chat_vision_json(
    text_prompt="识别图片中的缺陷",
    image_urls=["https://example.com/image.jpg"],
    expected_keys=["defect_type", "severity"]
)

# 流式输出
async for chunk in llm_client.stream_chat(messages=messages):
    if chunk["type"] == "content":
        yield chunk["text"]
```

**配置来源**（按优先级）：
1. 数据库配置（`core.llm_configs` 表）：管理员通过后台界面配置，支持加密存储 API key
2. 环境变量（仅开发环境）：`LLM_API_KEY`、`LLM_BASE_URL`、`LLM_MODEL`

生产环境必须在数据库中配置 LLM，否则会抛出 `LLMConfigError`。

**禁止用法**：
```python
# ❌ 直接使用 AIService
from app.platform.integrations.ai.client import AIService
ai = AIService(api_key="...", base_url="...", model="...")

# ❌ 使用 get_ai_service()
from app.platform.integrations.ai import get_ai_service
ai = get_ai_service()

# ❌ 手动读取环境变量构造客户端
api_key = os.getenv("AI_API_KEY", "")
ai = AIService(api_key=api_key, ...)
```

**异常处理**：
```python
from app.core.llm import llm_client, LLMOutputError, LLMProviderError, LLMRateLimitError

try:
    result = await llm_client.chat_json(messages=messages)
except LLMOutputError:
    logger.error("LLM 输出格式错误")
except LLMProviderError:
    logger.error("LLM 服务调用失败")
except LLMRateLimitError:
    logger.warning("LLM 速率限制")
```

## 配置管理规范

配置分两层：

**1. 部署配置**（Deployment Settings）
- 位置：`.env` 文件 + `core/config.py`
- 内容：API keys、数据库连接、飞书凭证等敏感信息
- 管理：平台管理员在部署时配置
- 变更频率：很少变更

**2. 运行时配置**（Runtime Settings）
- 位置：数据库 `core.module_settings` 表 + 各模块的 settings 页面
- 内容：模型名称、功能开关、调度参数等运营配置
- 管理：模块负责人通过 Web UI 管理
- 变更频率：经常变更

**读取配置**：
```python
# 运行时配置（从数据库）
from app.shared.config_reader import get_module_setting, get_module_setting_bool

model = await get_module_setting("safety", "SAFETY_AI_TEXT_MODEL", "deepseek-v4-flash")
enabled = await get_module_setting_bool("energy", "ENERGY_AUTO_COLLECT_ENABLED", False)

# 部署配置（从环境变量）
from app.core.config import get_settings
settings = get_settings()
api_key = settings.SAFETY_AI_TEXT_API_KEY
```

**新增配置**：
- API key / 凭证 → 加到 `core/config.py` 的 `Settings` 类
- 模型名称 / 功能开关 / 运营参数 → 加到 `scripts/seed_module_settings.py` 并通过 Web UI 管理

**禁止**：
- 在模块代码中使用 `os.getenv()` 读取运行时配置
- 将 API key 等凭证存入数据库
- 在 `core/config.py` 中存放模型名称等频繁变更的配置

## 模块结构

详见 [examples/module-structure.md](examples/module-structure.md)。

常用命令见 [examples/commands.md](examples/commands.md)。
