from functools import lru_cache
from typing import Annotated, Any, Optional

from pydantic import BeforeValidator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _coerce_bool(value: Any) -> Any:
    if isinstance(value, str):
        if value.lower() in ("true", "1", "yes", "on"):
            return True
        return False
    return value


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    APP_NAME: str = "dazah-backend"
    APP_ENV: str = "development"
    DEBUG: Annotated[bool, BeforeValidator(_coerce_bool)] = False
    SECRET_KEY: str = "change-me-in-production"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/dazah"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Audit
    AUDIT_RETENTION_DAYS: int = 7

    # API
    API_V1_PREFIX: str = "/api/v1"

    # Crawler (法规追踪爬虫)
    CRAWLER_HEADLESS: bool = True
    CRAWLER_BROWSERS_PATH: str = ""  # 空字符串 = Playwright 默认路径
    CDE_GUIDELINE_URL: str = "https://www.cde.org.cn/zdyz/listpage/9cd8db3b7530c6fa0c86485e563f93c7"
    DAILY_SYNC_CRON: str = "0 2 * * *"

    # Storage
    STORAGE_ROOT: str = "./storage"

    # LLM (AI 解析配置)
    LLM_API_KEY: Optional[str] = None
    LLM_BASE_URL: Optional[str] = "https://api.deepseek.com"
    LLM_MODEL: Optional[str] = "deepseek-chat"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
