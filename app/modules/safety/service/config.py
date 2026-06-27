"""Safety business workflows — AI 工作流配置 + AI 模型工厂."""

import logging
import os
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.safety.models import AIWorkflowConfig
from app.modules.safety.repository import SafetyRepository
from app.modules.safety.schemas import (
    AIWorkflowConfigCreate,
    AIWorkflowConfigUpdate,
)

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# AI 模型配置（从环境变量读取，支持部署时覆盖）
# ═══════════════════════════════════════════════════════════


def _get_ai_config() -> dict:
    """读取 AI 模型配置，环境变量优先，否则回退到硬编码默认值。"""
    return {
        "text": {
            "api_key": os.getenv("SAFETY_AI_TEXT_API_KEY", "sk-3b7d6bd5252246ff8af5f30a0f97b8f5"),
            "base_url": os.getenv("SAFETY_AI_TEXT_BASE_URL", "https://api.deepseek.com"),
            "model": os.getenv("SAFETY_AI_TEXT_MODEL", "deepseek-v4-flash"),
            "temperature": 0.1,
            "timeout": 120,
        },
        "vision": {
            "api_key": os.getenv("SAFETY_AI_VISION_API_KEY", "sk-a2ef55e9d2904572bb039f51e236a250"),
            "base_url": os.getenv("SAFETY_AI_VISION_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
            "model": os.getenv("SAFETY_AI_VISION_MODEL", "qwen-vl-max"),
            "temperature": 0.1,
            "timeout": 120,
        },
    }


def create_ai_service(config_type: str = "text"):
    """创建 AI 服务实例（硬编码配置，不依赖数据库）。

    config_type: "text"（文本模型）或 "vision"（视觉模型）
    """
    from app.platform.integrations.ai.client import AIService

    cfg = _get_ai_config().get(config_type)
    if not cfg:
        raise ValueError(f"不支持的 AI 配置类型: {config_type}，可选: text / vision")

    logger.debug("创建 AI 服务: config_type=%s model=%s", config_type, cfg["model"])
    return AIService(
        api_key=cfg["api_key"],
        base_url=cfg["base_url"],
        model=cfg["model"],
        timeout=cfg["timeout"],
    )


class ConfigService:
    """AI 工作流配置业务服务"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = SafetyRepository(session)

    # ==================== AI 工作流配置 CRUD ====================

    async def get_ai_workflow_configs(
        self,
        skip: int = 0,
        limit: int = 100,
        module_code: str | None = None,
        is_enabled: bool | None = None,
    ) -> tuple[list[AIWorkflowConfig], int]:
        """获取 AI 工作流配置列表"""
        return await self.repo.get_ai_workflow_configs(
            skip, limit, module_code, is_enabled
        )

    async def get_ai_workflow_config(self, config_id: uuid.UUID) -> AIWorkflowConfig | None:
        """获取 AI 工作流配置详情"""
        return await self.repo.get_ai_workflow_config_by_id(config_id)

    async def get_ai_workflow_config_by_module(
        self, module_code: str
    ) -> AIWorkflowConfig | None:
        """按模块代码获取 AI 工作流配置"""
        return await self.repo.get_ai_workflow_config_by_module(module_code)

    async def create_ai_workflow_config(self, data: AIWorkflowConfigCreate) -> AIWorkflowConfig:
        """创建 AI 工作流配置"""
        create_data = data.model_dump() if not isinstance(data, dict) else data
        return await self.repo.create_ai_workflow_config(create_data)

    async def update_ai_workflow_config(
        self, config_id: uuid.UUID, data: AIWorkflowConfigUpdate
    ) -> AIWorkflowConfig | None:
        """更新 AI 工作流配置"""
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        return await self.repo.update_ai_workflow_config(config_id, update_data)

    async def delete_ai_workflow_config(self, config_id: uuid.UUID) -> bool:
        """删除 AI 工作流配置"""
        return await self.repo.delete_ai_workflow_config(config_id)
