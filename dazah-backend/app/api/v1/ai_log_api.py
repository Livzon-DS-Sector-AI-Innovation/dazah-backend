"""AI 交互日志 API

提供 AI 日志查询和管理功能。
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.platform.database import get_db_session
from app.platform.ai.service import AiLogService

router = APIRouter()


# ============ Schema ============

class AiLogResponse(BaseModel):
    """AI 日志响应"""
    id: str
    bill_no: Optional[str] = None
    operate_type: str
    operator: str
    system_prompt: Optional[str] = None
    user_input: Optional[str] = None
    ai_response: Optional[str] = None
    error_message: Optional[str] = None
    tokens_used: Optional[int] = None
    latency_ms: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AiLogListResponse(BaseModel):
    """AI 日志列表响应"""
    items: list[AiLogResponse]
    total: int
    page: int
    page_size: int


# ============ API Endpoints ============

@router.get("/ai/logs", response_model=dict, summary="获取AI交互日志列表")
async def get_ai_logs(
    operate_type: Optional[str] = Query(None, description="操作类型"),
    operator: Optional[str] = Query(None, description="操作人"),
    keyword: Optional[str] = Query(None, description="关键字搜索"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    session: AsyncSession = Depends(get_db_session),
):
    """获取 AI 交互日志列表"""
    service = AiLogService(session)

    # 解析日期
    start_dt = None
    end_dt = None
    if start_date:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    if end_date:
        end_dt = datetime.strptime(end_date, "%Y-%m-%d") + datetime.timedelta(days=1)

    logs, total = await service.list_logs(
        operate_type=operate_type,
        operator=operator,
        start_date=start_dt,
        end_date=end_dt,
        page=page,
        page_size=page_size,
    )

    # 转换结果
    items = []
    for log in logs:
        item = AiLogResponse(
            id=str(log.id),
            bill_no=log.bill_no,
            operate_type=log.operate_type,
            operator=log.operator,
            system_prompt=log.system_prompt,
            user_input=log.user_input,
            ai_response=log.ai_response,
            error_message=log.error_message,
            tokens_used=log.tokens_used,
            latency_ms=log.latency_ms,
            created_at=log.created_at,
        )
        items.append(item)

    # 如果有关键字搜索，在结果中过滤
    if keyword:
        keyword_lower = keyword.lower()
        items = [
            item for item in items
            if (keyword_lower in (item.user_input or "").lower()
                or keyword_lower in (item.ai_response or "").lower()
                or keyword_lower in (item.operator or "").lower()
                or keyword_lower in (item.bill_no or "").lower())
        ]
        total = len(items)

    return {
        "code": 200,
        "message": "success",
        "data": {
            "items": [item.model_dump() for item in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    }


@router.get("/ai/logs/{log_id}", response_model=dict, summary="获取AI日志详情")
async def get_ai_log_by_id(
    log_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    """根据ID获取AI日志详情"""
    service = AiLogService(session)
    logs, _ = await service.list_logs(page=1, page_size=1)

    # 直接查询单条记录
    from sqlalchemy import text
    result = await session.execute(
        text("SELECT * FROM qms.qms_ai_log WHERE id = :id"),
        {"id": log_id}
    )
    log = result.fetchone()

    if not log:
        return {
            "code": 404,
            "message": "日志记录不存在",
            "data": None
        }

    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": str(log.id),
            "bill_no": log.bill_no,
            "operate_type": log.operate_type,
            "operator": log.operator,
            "system_prompt": log.system_prompt,
            "user_input": log.user_input,
            "ai_response": log.ai_response,
            "error_message": log.error_message,
            "tokens_used": log.tokens_used,
            "latency_ms": log.latency_ms,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
    }