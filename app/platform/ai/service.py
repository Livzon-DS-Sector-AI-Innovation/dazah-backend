"""AI chat service: build prompts and stream responses from Moonshot."""

from collections.abc import AsyncGenerator

import openai


class AiChatService:
    """Service for streaming chat completions via Moonshot API."""

    def __init__(self, api_key: str, model: str = "moonshot-v1-128k") -> None:
        self.client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.moonshot.cn/v1",
        )
        self.model = model

    async def stream_chat(
        self,
        messages: list[dict[str, any]],
        system_prompt: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """Stream chat completion tokens from the LLM.

        Messages may contain multimodal content (text + images) for models
        that support vision.
        """
        all_messages: list[dict[str, any]] = []
        if system_prompt:
            all_messages.append({"role": "system", "content": system_prompt})
        all_messages.extend(messages)

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=all_messages,  # type: ignore[arg-type]
            stream=True,
            temperature=0.1,   # 极低温度，禁止编造
            max_tokens=4096,
        )

        # When stream=True, the response is an AsyncStream; narrow the type.
        stream_resp: any = response
        async for chunk in stream_resp:
            delta = chunk.choices[0].delta.content if chunk.choices else None
            if delta:
                yield delta

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
            "6. 每次回答前，请先用 <think>...</think> 标签输出完整的思考过程，"
            "分析用户问题、检查查询结果、确认事实，然后再给出正式回答。\n\n"
        )

        if page:
            prompt += f"当前页面：{page}\n"

        return prompt

    @staticmethod
    def build_vehicle_system_prompt(page: str | None = None) -> str:
        """Build the system prompt for the vehicle assistant."""
        prompt = (
            "你是「小V」，原料药工厂车队管理智能助手。\n"
            "【绝对规则】\n"
            "1. 用户消息中【数据库查询结果】段落是系统从 PostgreSQL 实时查出的真实数据，"
            "是你回答的唯一依据。\n"
            "2. 如果查询结果中有用车申请、车辆信息等数据，你必须原样使用，"
            "一个字都不许改，不许补充，不许猜测。\n"
            "3. 如果查询结果明确写了'未找到'，请直接告知用户未找到相关记录。\n"
            "4. 禁止输出任何不在查询结果中的信息。\n"
            "5. 回答简洁，直接列事实。\n"
            "6. 当用户上传图片时，请根据图片内容协助分析（如识别用车单据、"
            "驾驶证、行驶证、车辆照片等），并结合数据库查询结果给出综合回答。\n"
            "7. 每次回答前，请先用 <think>...</think> 标签输出完整的思考过程，"
            "分析用户问题、检查查询结果、确认事实，然后再给出正式回答。\n\n"
        )

        if page:
            prompt += f"当前页面：{page}\n"

        return prompt
