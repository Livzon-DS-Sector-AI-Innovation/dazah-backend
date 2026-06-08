"""AI chat service: build prompts and stream responses from Moonshot."""

from collections.abc import AsyncGenerator
from typing import Any

import openai


class AiChatService:
    """Service for streaming chat completions via Moonshot API."""

    def __init__(self, api_key: str, model: str = "kimi-k2.5") -> None:
        self.client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.moonshot.cn/v1",
        )
        self.model = model

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

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=all_messages,  # type: ignore[arg-type]
            stream=True,
            temperature=1.0,  # 思考模式强制要求 1.0
            max_tokens=4096,
            extra_body={"thinking": {"type": "enabled"}},
        )

        # When stream=True, the response is an AsyncStream; narrow the type.
        stream: Any = response
        async for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            reasoning = getattr(delta, "reasoning_content", None)
            content = getattr(delta, "content", None)
            if reasoning:
                yield {"type": "reasoning", "text": reasoning}
            if content:
                yield {"type": "content", "text": content}

    @staticmethod
    def build_system_prompt(page: str | None = None) -> str:
        """Build the system prompt for the HR assistant."""
        prompt = (
            "你是「小H」，原料药工厂人事管理助手。\n"
            "【绝对规则】\n"
            "1. 用户消息中【数据库查询结果】段落是系统从 PostgreSQL 实时查出的真实数据，"
            "是你回答的唯一依据。\n"
            "2. 如果查询结果里有人名、部门、职位等信息，你必须原样使用，"
            "一个字都不许改，不许补充，不许猜测。\n"
            "3. 如果查询结果明确写了'未找到'，但你看到了'可能为相似姓名'的员工列表，"
            "请把这些相似姓名列出来，并提示用户核对姓名拼写。\n"
            "4. 禁止输出任何不在查询结果中的信息。\n"
            "5. 回答简洁，直接列事实。\n"
            "6. 系统支持多条件组合查询（如部门+状态+职位+性别+学历+年龄+入职日期等），"
            "如果用户问题涉及多个条件，查询结果已经过联合筛选，请直接基于筛选后的结果回答。\n"
            "7. 如果用户消息中包含【飞书多维表格查询结果】段落，"
            "这些是从飞书多维表格实时查询的真实数据，同样是回答的唯一依据。\n\n"
        )

        if page:
            prompt += f"当前页面：{page}\n"

        return prompt
