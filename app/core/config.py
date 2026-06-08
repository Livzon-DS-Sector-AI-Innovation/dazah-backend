from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
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

    # Feishu
    FEISHU_APP_ID: str = ""
    FEISHU_APP_SECRET: str = ""
    FEISHU_BITABLE_APP_TOKEN: str = ""
    FEISHU_BITABLE_EMPLOYEE_TABLE_ID: str = ""
    FEISHU_BITABLE_DEPARTMENT_TABLE_ID: str = ""
    FEISHU_BITABLE_OFFBOARDING_TABLE_ID: str = ""
    FEISHU_BITABLE_APPROVAL_TABLE_ID: str = ""
    FEISHU_BITABLE_VEHICLE_REQUEST_TABLE_ID: str = ""

    # AI
    MOONSHOT_API_KEY: str = ""

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
