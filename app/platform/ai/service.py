"""AI chat service: build prompts and stream responses from Moonshot."""

import json
import logging
from collections.abc import AsyncGenerator

import openai

logger = logging.getLogger(__name__)


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

    async def parse_resume(self, resume_text: str) -> dict[str, str]:
        """Parse resume text via LLM and extract structured fields."""
        system_prompt = (
            "你是一名专业的人力资源简历解析助手。请根据提供的简历文本，提取以下字段并返回严格的 JSON 格式：\n"
            '- gender: 性别（男/女，如未提及留空）\n'
            '- school: 毕业学校名称（如未提及留空）\n'
            '- education: 学历（如博士、硕士、本科、大专等，如未提及留空）\n'
            '- major: 专业（如未提及留空）\n'
            '- match_report: 候选人匹配度报告，以 HTML 格式输出对候选人综合能力的分析评价\n'
            '- recommendation_level: 推荐等级，只能为以下之一：强烈推荐、推荐、待定、不推荐\n'
            "注意：\n"
            "1. 只返回 JSON 对象，不要任何 markdown 代码块标记或其他说明文字。\n"
            '2. 所有字段都必须包含，没有信息时用空字符串""填充。\n'
            "3. match_report 用中文输出，包含对候选人教育背景、专业技能、工作经验的综合评价。"
        )
        messages = [
            {"role": "user", "content": f"请解析以下简历：\n\n{resume_text}"}
        ]

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system_prompt}, *messages],
                stream=False,
                temperature=1.0,
                max_tokens=4096,
            )
            content = response.choices[0].message.content or ""
            # Clean up markdown code block if present
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            result = json.loads(content)
            return {
                "gender": result.get("gender", ""),
                "school": result.get("school", ""),
                "education": result.get("education", ""),
                "major": result.get("major", ""),
                "match_report": result.get("match_report", ""),
                "recommendation_level": result.get("recommendation_level", ""),
            }
        except Exception:
            logger.exception("Failed to parse resume via LLM")
            return {
                "gender": "",
                "school": "",
                "education": "",
                "major": "",
                "match_report": "",
                "recommendation_level": "",
            }

    async def parse_resume_from_images(
        self,
        images: list[bytes],
        position: str,
    ) -> dict[str, str]:
        """Parse resume images via vision-capable LLM and extract structured fields + match report."""
        import base64

        system_prompt = (
            "你是一名专业的人力资源简历解析与岗位匹配评估助手。请根据提供的简历图片，执行以下两项任务并返回严格的 JSON 格式：\n\n"
            "**任务一：信息提取**\n"
            "从简历中提取以下字段：\n"
            '- gender: 性别（男/女，如未提及留空）\n'
            '- school: 毕业学校名称（如未提及留空）\n'
            '- education: 学历（如博士、硕士、本科、大专等，如未提及留空）\n'
            '- major: 专业（如未提及留空）\n\n'
            "**任务二：匹配度报告生成**\n"
            "基于提取的简历信息与用户提供的应聘职位，生成匹配度报告。报告必须严格遵循以下模板与规则：\n\n"
            "【必填信息】\n"
            "- 姓名、学历必填；缺失必填项时返回错误提示\n"
            "- 信息格式必须规范\n\n"
            "【安全要求】\n"
            "- 不输出个人敏感信息\n"
            "- 不泄露公司机密信息\n"
            "- 保持客观中立描述\n\n"
            "【输出规范】\n"
            "1. 格式要求：\n"
            "   - 不使用#、##、###等标题标记\n"
            "   - 使用**加粗文本**代替标题\n"
            "   - 列表统一使用-符号\n\n"
            "2. 评分标准：\n"
            "   - 所有评分必须有事实依据\n"
            "   - 禁止主观臆断\n"
            "   - 信息不足标记为'待评估'\n"
            "   - 推荐等级限定为：强烈推荐/推荐/待定/不推荐\n\n"
            "3. 一致性要求：\n"
            "   - 板块顺序固定不变\n"
            "   - 评价描述客观专业\n"
            "   - 用语保持一致性\n"
            "   - 禁止过度修饰词\n"
            "   - 严格遵循模板结构\n"
            "   - 禁止扩写或添加额外内容\n"
            "   - 禁止添加模板中未定义的板块\n"
            "   - 禁止对模板结构进行任何形式的扩展\n"
            "   - 输出内容包含：候选人信息卡片、匹配度总评、能力维度评估\n"
            "   - 其中能力维度评估包含：专业能力、基础匹配、发展潜力、软实力\n"
            "   - 除以上内容，禁止生成任何额外的信息（如补充说明、差异分析等）\n"
            "   - 输出内容必须与模板一一对应\n\n"
            "4. 标签规范：\n"
            "   - 颜色标签固定搭配\n"
            "   - emoji固定使用\n\n"
            "【推荐等级规则】\n"
            "- <text_tag color='green'>强烈推荐</text_tag>：核心要求全部满足，无显著差距\n"
            "- <text_tag color='blue'>推荐</text_tag>：核心要求基本满足，差距可接受\n"
            "- <text_tag color='yellow'>待定</text_tag>：部分要求满足，关键点待确认\n"
            "- <text_tag color='red'>不推荐</text_tag>：核心要求存在明显差距\n\n"
            "【核心评价规则】\n"
            "1. 评价结构：{具体经验说明}，但{差距说明}；{待确认事项}\n"
            "2. 内容要求：\n"
            "   - 第一部分：以'具备'开头，说明与岗位直接相关的具体经验（15字内）\n"
            "   - 第二部分：以'但'字连接，指出与岗位要求的明确差距（15字内）\n"
            "   - 第三部分：以'；'分隔，以'需'字说明待确认事项（10字内）\n"
            "   - 总字数不超过40字\n"
            "   - 保持客观中立，避免主观评价词\n"
            "   - 每个部分必须具体明确\n\n"
            "【匹配度报告模板】\n\n"
            "**一、候选人信息卡片**\n"
            "👤 姓名：{姓名}\n"
            "🎓 学历：{最高学历} | {毕业院校} | {专业}\n"
            "💼 当前职位：{职位}\n"
            "🔮 期望发展：{期望职位} | {期望地点}\n"
            "📝 核心技能：{技能1}、{技能2}、{技能3}\n"
            "---\n"
            "**二、匹配度评估** <text_tag color='blue'>概览</text_tag>\n"
            "📋 **推荐等级**：<text_tag color='green/blue/yellow/red'>{强烈推荐/推荐/待定/不推荐}</text_tag>\n"
            "💬 **核心评价**：{具体经验说明}，但{差距说明}；{待确认事项}\n"
            "---\n"
            "**三、能力维度评估**\n"
            "**专业能力** <text_tag color='red'>核心</text_tag>\n"
            "- 技术栈：{技能评价}\n"
            "- 项目经验：{经验评价}\n\n"
            "**基础匹配** <text_tag color='green'>基础</text_tag>\n"
            "- 学历背景：✅/⚠️/❌ {说明}\n"
            "- 专业背景：✅/⚠️/❌ {说明}\n\n"
            "**发展潜力** <text_tag color='orange'>潜力</text_tag>\n"
            "- 成长性：{评价}\n"
            "- 稳定性：{评价}\n\n"
            "**软实力** <text_tag color='purple'>软实力</text_tag>\n"
            "- 沟通协作：{评价}\n"
            "- 执行力：{评价}\n\n"
            "【JSON 输出格式】\n"
            "必须且只能返回以下 JSON 对象，不要任何 markdown 代码块标记或其他说明文字：\n"
            '{\n'
            '  "gender": "...",\n'
            '  "school": "...",\n'
            '  "education": "...",\n'
            '  "major": "...",\n'
            '  "match_report": "...",\n'
            '  "recommendation_level": "..."\n'
            '}\n'
            "所有字段都必须包含，没有信息时用空字符串\"\"填充。"
        )

        # Build message content with images
        content: list[dict[str, Any]] = [
            {
                "type": "text",
                "text": f"请解析以下简历图片，并评估其与应聘职位「{position}」的匹配度。",
            }
        ]
        for img_bytes in images:
            b64 = base64.b64encode(img_bytes).decode("utf-8")
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{b64}"},
                }
            )

        messages = [{"role": "user", "content": content}]

        logger.info(
            "Sending vision request to Moonshot: model=%s, images=%d, position=%s",
            self.model,
            len(images),
            position,
        )
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system_prompt}, *messages],
                stream=False,
                temperature=1.0,
                max_tokens=4096,
            )
            raw_content = response.choices[0].message.content or ""
            logger.info("Moonshot vision response received, length=%d", len(raw_content))
            # Clean up markdown code block if present
            raw_content = raw_content.strip()
            if raw_content.startswith("```json"):
                raw_content = raw_content[7:]
            if raw_content.startswith("```"):
                raw_content = raw_content[3:]
            if raw_content.endswith("```"):
                raw_content = raw_content[:-3]
            raw_content = raw_content.strip()
            logger.debug("Cleaned response: %s", raw_content[:500])
            result = json.loads(raw_content)
            return {
                "gender": result.get("gender", ""),
                "school": result.get("school", ""),
                "education": result.get("education", ""),
                "major": result.get("major", ""),
                "match_report": result.get("match_report", ""),
                "recommendation_level": result.get("recommendation_level", ""),
            }
        except Exception as exc:
            # Log detailed error for debugging
            error_body = ""
            if hasattr(exc, "response") and hasattr(exc.response, "text"):
                error_body = exc.response.text
            elif hasattr(exc, "body"):
                error_body = str(exc.body)
            logger.error(
                "Failed to parse resume images via LLM: %s. Response: %s",
                exc,
                error_body,
            )
            return {
                "gender": "",
                "school": "",
                "education": "",
                "major": "",
                "match_report": "",
                "recommendation_level": "",
            }
