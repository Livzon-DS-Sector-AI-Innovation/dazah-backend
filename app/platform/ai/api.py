"""AI platform API routes."""

import json
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.platform.ai.deps import get_ai_chat_service
from app.platform.ai.schemas import ChatRequest
from app.platform.ai.service import AiChatService

router = APIRouter()


@router.post("/chat/stream", summary="AI 流式对话")
async def chat_stream(
    request: ChatRequest,
    service: AiChatService = Depends(get_ai_chat_service),
) -> StreamingResponse:
    """Receive a chat request and stream the AI response via SSE."""

    system_prompt = AiChatService.build_system_prompt(
        page=request.page_context.page if request.page_context else None
    )

    # Append page context as the last user message hint if provided
    messages = [m.model_dump() for m in request.messages]
    if request.page_context and request.page_context.data_summary:
        summary_text = json.dumps(
            request.page_context.data_summary, ensure_ascii=False
        )
        # Only inject when the last message is from user
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
