"""AI module dependencies."""

from app.core.config import get_settings
from app.platform.ai.service import AiChatService


async def get_ai_chat_service() -> AiChatService:
    settings = get_settings()
    return AiChatService(api_key=settings.MOONSHOT_API_KEY)
