"""AI chat service: build prompts and stream responses from Moonshot."""

from collections.abc import AsyncGenerator
from typing import Any

import openai


class AiChatService:
    """Service for streaming chat completions via Moonshot API."""

    def __init__(self, api_key: str, model: str = "moonshot-v1-8k") -> None:
        self.client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.moonshot.cn/v1",
        )
        self.model = model

    async def stream_chat(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """Stream chat completion tokens from the LLM."""
        all_messages: list[dict[str, str]] = []
        if system_prompt:
            all_messages.append({"role": "system", "content": system_prompt})
        all_messages.extend(messages)

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=all_messages,  # type: ignore[arg-type]
            stream=True,
            temperature=0.7,
        )

        # When stream=True, the response is an AsyncStream; narrow the type.
        stream: Any = response
        async for chunk in stream:
            delta = chunk.choices[0].delta.content if chunk.choices else None
            if delta:
                yield delta

    @staticmethod
    def build_system_prompt(page: str | None = None) -> str:
        """Build the system prompt for the HR assistant."""
        prompt = (
            "你是一位原料药工厂的人事管理智能助手，名叫「小智」。\n"
            "你可以帮助用户查询、整理和分析人事数据，并给出简单的管理建议。\n"
            "请遵守以下规则：\n"
            "1. 回答简洁专业，使用中文。\n"
            "2. 涉及敏感个人信息（身份证号、银行卡号、手机号、家庭地址）时，"
            "只做统计或脱敏处理，不直接输出完整原始值。\n"
            "3. 如果用户问题与当前页面数据相关，优先基于页面上下文回答。\n"
            "4. 不确定的问题请如实说明，不编造数据。\n\n"
            "可用数据表结构：\n"
            "- employees: 员工档案（工号、姓名、部门、班组、职位、"
            "职类、级别、性别、籍贯、学历、学校、专业、"
            "入职日期、参加工作时间、厂龄、司龄、工作年限、"
            "合同期限与日期、状态:在职/离职/试用期/待审批、"
            "职称/职业资格、培训档案编号、飞书同步状态）\n"
            "- departments: 部门信息（部门名称、编码、描述）\n"
            "- teams: 班组信息（班组名称、编码、所属部门）\n"
            "- offboarding_records: 离职记录（离职日期、类型、原因、交接状态）\n"
        )

        if page:
            prompt += f"\n用户当前所在页面：{page}\n"

        return prompt
