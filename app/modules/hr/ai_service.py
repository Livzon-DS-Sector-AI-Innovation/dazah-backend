"""AI chat service for HR turnover analysis.

Uses core.llm for streaming completions.
"""

from collections.abc import AsyncGenerator
from app.core.llm import llm_client
from app.core.config import get_settings
from app.shared.config_reader import get_module_setting


class AiChatService:
    """Service for streaming chat completions via core.llm."""

    def __init__(self, api_key: str = None, model: str = None) -> None:
        # api_key and model are ignored - using core.llm config
        pass

    async def stream_chat(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
    ) -> AsyncGenerator[dict[str, str], None]:
        """Stream chat completion tokens from the LLM.

        Yields dicts with keys:
            - type: "reasoning" | "content"
            - text: the token text
        """
        all_messages: list[dict[str, str]] = []
        if system_prompt:
            all_messages.append({"role": "system", "content": system_prompt})
        all_messages.extend(messages)

        async for chunk in llm_client.stream_chat(messages=all_messages):
            yield chunk

    @staticmethod
    async def build_system_prompt(page: str | None = None) -> str:
        """Build the system prompt for the HR assistant."""
        prompt = await get_module_setting(
            "hr", 
            "AI_SYSTEM_PROMPT", 
            "你是「小H」，原料药工厂人事管理助手。只基于查询结果回答人事问题，禁止编造。回答极其简洁，只陈述事实，不分析、不解释、不推理。"
        )

        if page:
            prompt += f"\n当前页面：{page}"

        return prompt
