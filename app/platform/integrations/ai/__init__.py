"""AI/LLM integration adapter for OpenAI-compatible APIs."""

from app.platform.integrations.ai.client import AIService, AIOutputError

__all__ = ["AIService", "AIOutputError"]
