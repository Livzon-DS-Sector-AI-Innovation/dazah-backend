"""AI platform API routes."""

import json
import re
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.hr.public_api import (
    count_employees,
    list_employees_by_department,
    search_employees_by_name,
    search_employees_fuzzy,
)
from app.platform.ai.deps import get_ai_chat_service
from app.platform.ai.schemas import ChatRequest
from app.platform.ai.service import AiChatService

router = APIRouter()


def _extract_names(text: str) -> list[str]:
    """Extract possible Chinese person names from text (2-4 chars)."""
    return re.findall(r"[一-龥]{2,4}", text)


def _detect_query_intent(text: str) -> tuple[str, dict] | None:
    """Detect user intent for HR database queries."""
    # 1. 某部门有哪些人 / 某部门的人 / 某部门名单
    m = re.search(
        r"([一-龥\w\-]{2,20}(?:部门|车间|科室|组|部|中心))"
        r".*?(?:有哪些人|的人|名单|员工|成员)",
        text,
    )
    if m:
        return ("list_department", {"department": m.group(1)})

    # 2. 某人（是/在）哪个部门
    m = re.search(
        r"([一-龥]{2,4})(?:是|在).*?(?:哪个部门|什么部门|所属部门)",
        text,
    )
    if m:
        return ("employee_department", {"name": m.group(1)})

    # 3. 某部门有多少（人/员工）
    m = re.search(
        r"([一-龥\w\-]{2,20}(?:部门|车间|科室|组|部|中心))"
        r".*?(?:有多少|共多少|人数|几人)",
        text,
    )
    if m:
        return ("count_department", {"department": m.group(1)})

    # 4. 总共有多少（人/员工）
    if re.search(
        r"(?:总共|一共|全厂|公司|整体).*?(?:有多少|共多少|人数|几人)",
        text,
    ):
        return ("count_total", {})

    return None


async def _build_db_context(
    session: AsyncSession, text: str
) -> str:
    """Query HR database based on user intent and return formatted context."""
    parts: list[str] = []

    # Intent-based queries
    intent = _detect_query_intent(text)
    if intent:
        action, params = intent
        if action == "list_department":
            dept = params["department"]
            employees, total = await list_employees_by_department(session, dept)
            if employees:
                parts.append(f"【数据库查询结果】{dept}共有{total}名员工：")
                for emp in employees:
                    parts.append(
                        f"- {emp['name']}（工号:{emp['employee_number']}）"
                        f"，职位:{emp['position']}"
                        f"，状态:{emp['status']}"
                    )
            else:
                parts.append(f"【数据库查询结果】未找到{dept}的员工记录。")

        elif action == "employee_department":
            name = params["name"]
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
                # 精确查询不到时，做模糊查询
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

        elif action == "count_department":
            dept = params["department"]
            total = await count_employees(session, department=dept)
            parts.append(f"【数据库查询结果】{dept}共有{total}名员工。")

        elif action == "count_total":
            total = await count_employees(session)
            parts.append(f"【数据库查询结果】全厂共有{total}名员工。")

    # Fallback: keyword-based name search if no intent matched
    if not intent:
        names = _extract_names(text)
        seen: set[str] = set()
        for name in names[:3]:
            if name in seen:
                continue
            seen.add(name)
            employees = await search_employees_by_name(session, name)
            if employees:
                parts.append(
                    f"【数据库查询结果】姓名包含'{name}'的员工："
                )
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
        db_context = await _build_db_context(session, user_text)

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
        async for token in service.stream_chat(messages, system_prompt):
            payload = json.dumps({"content": token}, ensure_ascii=False)
            yield f"data: {payload}\n\n"
        done_payload = json.dumps({"done": True}, ensure_ascii=False)
        yield f"data: {done_payload}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )
