"""AI module dependencies."""

from fastapi import HTTPException, status

from app.core.config import get_settings
from app.platform.ai.service import AiChatService


async def get_ai_chat_service() -> AiChatService:
    settings = get_settings()
    api_key = settings.MOONSHOT_API_KEY
    model = settings.AI_MODEL
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI 服务未配置：MOONSHOT_API_KEY 缺失",
        )
    return AiChatService(api_key=api_key, model=model)
