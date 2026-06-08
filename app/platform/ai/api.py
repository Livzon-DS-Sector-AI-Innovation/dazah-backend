"""AI platform API routes."""

import json
import logging
import uuid
from collections.abc import AsyncGenerator

import openai
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.hr.public_api import (
    count_employees,
    query_employees,
    search_employees_by_name,
    search_employees_fuzzy,
)
from app.platform.ai.deps import get_ai_chat_service
from app.platform.ai.executor import execute_plan, format_step_results
from app.platform.ai.feishu_context import build_feishu_context
from app.platform.ai.planner import generate_plan
from app.platform.ai.query_parser import describe_filters, parse_employee_query
from app.platform.ai.query_parser_llm import parse_with_llm
from app.platform.ai.schemas import ChatRequest
from app.platform.ai.service import AiChatService

router = APIRouter()
logger = logging.getLogger(__name__)


def _extract_names(text: str) -> list[str]:
    """Extract possible Chinese person names from text (2-4 chars)."""
    import re

    matches = re.findall(r"[一-龥]{2,4}", text)
    exclude = {
        "员工",
        "人员",
        "人事",
        "工厂",
        "公司",
        "部门",
        "车间",
        "科室",
        "班组",
        "团队",
        "职位",
        "岗位",
        "状态",
        "性别",
        "学历",
        "年龄",
        "工龄",
        "司龄",
        "厂龄",
        "入职",
        "离职",
        "试用",
        "合同",
        "统计",
        "查询",
        "查找",
        "搜索",
        "有多少",
        "共多少",
        "多少个",
        "工程师",
        "经理",
        "主管",
        "专员",
        "操作员",
        "操作工",
        "文员",
        "会计",
        "出纳",
        "司机",
        "保安",
        "厨师",
        "保洁",
        "电工",
        "焊工",
        "钳工",
        "车工",
        "铣工",
        "磨工",
        "叉车工",
        "搬运工",
        "包装工",
        "技术员",
        "质检员",
        "安全员",
        "消防员",
        "仓管员",
        "物料员",
        "统计员",
        "计划员",
        "调度员",
        "采购员",
        "销售员",
        "业务员",
        "客服",
        "前台",
        "班长",
        "组长",
        "厂长",
        "总监",
        "助理",
        "秘书",
        "顾问",
        "研究员",
    }
    return [m for m in matches if m not in exclude]


async def _build_db_context(
    session: AsyncSession,
    client: openai.AsyncOpenAI | None,
    text: str,
) -> str:
    """Query HR database based on natural language and return formatted context.

    Three-layer architecture:
        1. Planner: generate execution plan from user intent
        2. Executor: execute plan step by step (parallel within each step)
        3. Context Builder: format results into natural-language context

    Falls back to legacy parsing if the planner fails.
    """
    parts: list[str] = []

    # Layer 1 + 2: Try the new planner/executor architecture first
    plan_executed = False
    if client is not None:
        try:
            plan = await generate_plan(client, text)
            if plan and plan.needs_data and plan.steps:
                logger.info(
                    "Planner generated %d-step plan for: %s",
                    len(plan.steps),
                    text,
                )
                step_results = await execute_plan(
                    session, plan, text, client
                )
                formatted = format_step_results(step_results)
                if formatted:
                    parts.append("【数据库查询结果】")
                    parts.append(formatted)
                    plan_executed = True
            elif plan and not plan.needs_data:
                logger.info("Planner decided no data needed for: %s", text)
        except Exception as exc:
            logger.warning("Three-layer plan execution failed: %s", exc)

    # Fallback: legacy parsing if planner did not produce results
    if not plan_executed:
        logger.info("Falling back to legacy parsing for: %s", text)

        # 1. Try LLM-based parsing first
        criteria = None
        if client is not None:
            try:
                criteria = await parse_with_llm(client, text)
                logger.info(
                    "LLM intent parsed: filters=%s type=%s",
                    criteria.filters if criteria else None,
                    criteria.query_type if criteria else None,
                )
            except Exception as exc:
                logger.warning("LLM intent parsing failed: %s", exc)
                criteria = None

        # 2. Fallback to hardcoded regex parser
        if criteria is None:
            criteria = parse_employee_query(text)
            logger.info(
                "Fallback regex parsed: filters=%s",
                criteria.filters if criteria else None,
            )

        # 3. Execute query if we have criteria
        if criteria and criteria.filters:
            desc = describe_filters(criteria.filters)
            if criteria.query_type == "count":
                total = await count_employees(session, filters=criteria.filters)
                parts.append(f"【数据库查询结果】{desc}共有{total}名员工。")
            else:
                employees, total = await query_employees(
                    session, filters=criteria.filters, page=1, page_size=200
                )
                if employees:
                    parts.append(
                        f"【数据库查询结果】{desc}共有{total}名员工，以下是部分信息："
                    )
                    for emp in employees[:50]:
                        info_parts = [
                            f"- {emp['name']}（工号:{emp['employee_number']}）",
                            f"部门:{emp['department']}",
                            f"职位:{emp['position']}",
                            f"状态:{emp['status']}",
                        ]
                        if emp.get("team"):
                            info_parts.append(f"班组:{emp['team']}")
                        if emp.get("gender"):
                            info_parts.append(f"性别:{emp['gender']}")
                        if emp.get("education"):
                            info_parts.append(f"学历:{emp['education']}")
                        if emp.get("age"):
                            info_parts.append(f"年龄:{emp['age']}")
                        if emp.get("hire_date"):
                            info_parts.append(f"入职日期:{emp['hire_date']}")
                        parts.append("，".join(info_parts))
                else:
                    parts.append(f"【数据库查询结果】未找到{desc}的员工记录。")

        # 4. Fallback: name-based search if no structured criteria matched
        if not criteria or (not criteria.filters and criteria.name_keyword):
            names = _extract_names(text)
            seen: set[str] = set()
            for name in names[:3]:
                if name in seen:
                    continue
                seen.add(name)
                employees = await search_employees_by_name(session, name)
                if employees:
                    parts.append(f"【数据库查询结果】姓名包含'{name}'的员工：")
                    for emp in employees:
                        parts.append(
                            f"- {emp['name']}（工号:{emp['employee_number']}）"
                            f"，部门:{emp['department']}"
                            f"，职位:{emp['position']}"
                            f"，状态:{emp['status']}"
                        )
                else:
                    fuzzy = await search_employees_fuzzy(session, name)
                    if fuzzy:
                        parts.append(
                            f"【数据库查询结果】未找到姓名包含'{name}'的员工。"
                            f"以下是名字中包含'{name}'中某个字的员工（可能为相似姓名）："
                        )
                        for emp in fuzzy[:10]:
                            parts.append(
                                f"- {emp['name']}（工号:{emp['employee_number']}）"
                                f"，部门:{emp['department']}"
                                f"，职位:{emp['position']}"
                                f"，状态:{emp['status']}"
                            )
                    else:
                        parts.append(
                            f"【数据库查询结果】未找到姓名包含'{name}'或相关字的员工。"
                        )

    # 5. Feishu Bitable query (server-side filtered)
    feishu_context = await build_feishu_context(text)
    if feishu_context:
        parts.append(feishu_context)

    return "\n".join(parts)


@router.post("/chat/stream", summary="AI 流式对话")
async def chat_stream(
    request: ChatRequest,
    service: AiChatService = Depends(get_ai_chat_service),
    session: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Receive a chat request and stream the AI response via SSE."""

    # 1. Build base system prompt
    system_prompt = AiChatService.build_system_prompt(
        page=request.page_context.page if request.page_context else None
    )

    # 2. Query database based on user intent
    db_context = ""
    if request.messages and request.messages[-1].role == "user":
        user_text = request.messages[-1].content
        db_context = await _build_db_context(
            session, service.client, user_text
        )

    # 3. Build messages list
    messages = [m.model_dump() for m in request.messages]

    # Inject DB context directly into the last user message
    if db_context and messages and messages[-1]["role"] == "user":
        original = messages[-1]["content"]
        messages[-1]["content"] = (
            f"【数据库查询结果，请严格基于以下事实回答，禁止编造】\n"
            f"{db_context}\n\n"
            f"【用户原始问题】\n{original}"
        )

    # 4. Append page context as the last user message hint if provided
    if request.page_context and request.page_context.data_summary:
        summary_text = json.dumps(
            request.page_context.data_summary, ensure_ascii=False
        )
        if messages and messages[-1]["role"] == "user":
            original = messages[-1]["content"]
            messages[-1]["content"] = (
                f"[当前页面数据概览]\n{summary_text}\n\n"
                f"[用户问题]\n{original}"
            )

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            async for chunk in service.stream_chat(messages, system_prompt):
                if chunk["type"] == "reasoning":
                    payload = json.dumps(
                        {"reasoning_content": chunk["text"]}, ensure_ascii=False
                    )
                else:
                    payload = json.dumps({"content": chunk["text"]}, ensure_ascii=False)
                yield f"data: {payload}\n\n"
            done_payload = json.dumps({"done": True}, ensure_ascii=False)
            yield f"data: {done_payload}\n\n"
        except Exception:
            import logging

            logger = logging.getLogger(__name__)
            logger.exception("AI stream chat failed")
            error_payload = json.dumps(
                {"error": True, "message": "AI 服务暂时不可用，请稍后重试"},
                ensure_ascii=False,
            )
            yield f"data: {error_payload}\n\n"
            done_payload = json.dumps({"done": True}, ensure_ascii=False)
            yield f"data: {done_payload}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )


