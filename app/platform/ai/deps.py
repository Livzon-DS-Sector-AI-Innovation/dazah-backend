"""AI module dependencies."""

from app.core.config import get_settings
from app.platform.ai.service import AiChatService


async def get_ai_chat_service() -> AiChatService | None:
    settings = get_settings()
    api_key = settings.MOONSHOT_API_KEY
    if not api_key:
        return None
    return AiChatService(api_key=api_key)
