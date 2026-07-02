from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    APP_NAME: str = "dazah-backend"
    APP_ENV: str = "development"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/dazah"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Audit
    AUDIT_RETENTION_DAYS: int = 7

    # API
    API_V1_PREFIX: str = "/api/v1"

    # Audit
    AUDIT_RETENTION_DAYS: int = 7

    # Feishu primary bot (recruitment / HR ledger)
    FEISHU_BOT_NAME: str = ""
    FEISHU_APP_ID: str = ""
    FEISHU_APP_SECRET: str = ""
    FEISHU_BITABLE_APP_TOKEN: str = ""
    FEISHU_BITABLE_EMPLOYEE_TABLE_ID: str = ""
    FEISHU_BITABLE_DEPARTMENT_TABLE_ID: str = ""
    FEISHU_BITABLE_OFFBOARDING_TABLE_ID: str = ""
    FEISHU_BITABLE_ONBOARDING_TABLE_ID: str = ""
    FEISHU_BITABLE_DEPARTURE_TABLE_ID: str = ""
    FEISHU_BITABLE_APPROVAL_TABLE_ID: str = ""
    FEISHU_BITABLE_CANDIDATE_APP_TOKEN: str = ""
    FEISHU_BITABLE_CANDIDATE_TABLE_ID: str = ""

    # Feishu vehicle bot (administration)
    FEISHU_VEHICLE_APP_ID: str = ""
    FEISHU_VEHICLE_APP_SECRET: str = ""
    FEISHU_BITABLE_VEHICLE_REQUEST_APP_TOKEN: str = ""
    FEISHU_BITABLE_VEHICLE_REQUEST_TABLE_ID: str = ""

    # Feishu training bot (training notification / product / material BOM)
    FEISHU_TRAINING_APP_ID: str = ""
    FEISHU_TRAINING_APP_SECRET: str = ""
    FEISHU_BITABLE_TRAINING_NOTIFICATION_APP_TOKEN: str = ""
    FEISHU_BITABLE_TRAINING_NOTIFICATION_TABLE_ID: str = ""
    FEISHU_BITABLE_PRODUCT_APP_TOKEN: str = ""
    FEISHU_BITABLE_PRODUCT_TABLE_ID: str = ""
    FEISHU_BITABLE_MATERIAL_BOM_APP_TOKEN: str = ""
    FEISHU_BITABLE_MATERIAL_BOM_TABLE_ID: str = ""

    # Feishu AI Query
    FEISHU_AI_QUERY_TABLES: str = ""  # JSON: {"别名": {"app_token": "...", "table_id": "...", "filterable_fields": [...]}}
    FEISHU_AI_QUERY_MAX_ROWS: int = 200

    # Aily
    AILY_APP_ID: str = ""

    # AI
    MOONSHOT_API_KEY: str = ""
    AI_MODEL: str = "kimi-k2.5"
    AI_SYSTEM_PROMPT: str = (
        "你是「小H」，原料药工厂人事管理助手。"
        "只基于查询结果回答人事问题，禁止编造。"
        "回答极其简洁，只陈述事实，不分析、不解释、不推理。"
        "禁止出现'根据规则'、'依据以上信息'等元话语。"
    )

    # 前端地址（用于飞书卡片/通知里的深链跳转，无请求上下文时使用）
    FRONTEND_URL: str = "http://localhost:3000"

    # 安全模块 AI 模型（文本 + 视觉，OpenAI 兼容；密钥只进本地 .env）
    SAFETY_AI_TEXT_API_KEY: str = ""
    SAFETY_AI_TEXT_BASE_URL: str = "https://api.deepseek.com"
    SAFETY_AI_TEXT_MODEL: str = "deepseek-chat"
    SAFETY_AI_VISION_API_KEY: str = ""
    SAFETY_AI_VISION_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    SAFETY_AI_VISION_MODEL: str = "qwen-vl-max"
    SAFETY_AI_TIMEOUT: int = 120

    # 安全模块飞书（独立应用 + 隐患多维表格，未配置时自动跳过同步）
    SAFETY_FEISHU_APP_ID: str = ""
    SAFETY_FEISHU_APP_SECRET: str = ""
    SAFETY_FEISHU_BITABLE_APP_TOKEN: str = ""
    SAFETY_FEISHU_BITABLE_HAZARD_TABLE_ID: str = ""

    # 安全/设备模块飞书群通知 chat_id（定时任务推送目标）
    FEISHU_SAFETY_CHAT_ID: str = ""
    FEISHU_EQUIPMENT_CHAT_ID: str = ""

    # 设备模块飞书交互机器人（独立凭证，用于巡检通知/交互式巡检）
    EQUIPMENT_FEISHU_APP_ID: str = ""
    EQUIPMENT_FEISHU_APP_SECRET: str = ""
    EQUIPMENT_FEISHU_WS_ENABLED: bool = False

    # 设备模块巡检 AI 视觉分析（OpenAI 兼容，未配置 API_KEY 时 AI 端点返回明确错误）
    EQUIPMENT_AI_VISION_API_KEY: str = ""
    EQUIPMENT_AI_VISION_BASE_URL: str = (
        "https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    EQUIPMENT_AI_VISION_MODEL: str = "qwen-vl-max"
    EQUIPMENT_AI_TIMEOUT: int = 120

    # MinIO 对象存储（巡检照片等），默认关闭走本地存储
    MINIO_ENABLED: bool = False
    MINIO_ENDPOINT: str = ""
    MINIO_ACCESS_KEY: str = ""
    MINIO_SECRET_KEY: str = ""
    MINIO_BUCKET_PREFIX: str = "dazah"
    MINIO_SECURE: bool = False
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
