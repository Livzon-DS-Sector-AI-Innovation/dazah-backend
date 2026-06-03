"""维修工单 API 路由."""

import uuid

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import CurrentUser
from app.core.exceptions import AppException
from app.core.response import paginated_response, success_response
from app.modules.equipment import service
from app.modules.equipment.schemas import (
    WorkOrderAssign,
    WorkOrderComplete,
    WorkOrderCreate,
    WorkOrderResponse,
    WorkOrderStatistics,
    WorkOrderVerify,
)


def _require_user(current_user: CurrentUser) -> uuid.UUID:
    """要求已认证用户，返回用户ID"""
    if not current_user:
        raise AppException(message="需要登录才能执行此操作", status_code=401)
    return current_user.id

router = APIRouter()


@router.post("/", summary="创建工单（报修）")
async def create_work_order(
    data: WorkOrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    reporter_id = _require_user(current_user)
    wo = await service.create_work_order(db, data, reporter_id)
    return success_response(data=WorkOrderResponse.model_validate(wo))


@router.get("/", summary="工单列表")
async def list_work_orders(
    status: str | None = Query(None, description="工单状态"),
    equipment_id: uuid.UUID | None = Query(None, description="设备ID"),
    priority: str | None = Query(None, description="优先级"),
    order_type: str | None = Query(None, description="工单类型"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=200, description="每页数量"),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    work_orders, total = await service.get_work_orders(
        db, status=status, equipment_id=equipment_id,
        priority=priority, order_type=order_type,
        page=page, page_size=page_size,
    )
    return paginated_response(
        data=[WorkOrderResponse.model_validate(wo) for wo in work_orders],
        page=page, page_size=page_size, total=total,
    )


@router.get("/statistics", summary="工单统计")
async def get_work_order_statistics(
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    stats = await service.get_work_order_statistics(db)
    return success_response(data=WorkOrderStatistics.model_validate(stats))


@router.get("/{work_order_id}", summary="工单详情")
async def get_work_order(
    work_order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    wo = await service.get_work_order_by_id(db, work_order_id)
    return success_response(data=WorkOrderResponse.model_validate(wo))


@router.put("/{work_order_id}/assign", summary="指派维修人")
async def assign_work_order(
    work_order_id: uuid.UUID,
    data: WorkOrderAssign,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    wo = await service.assign_work_order(db, work_order_id, data.assignee_id)
    return success_response(data=WorkOrderResponse.model_validate(wo))


@router.put("/{work_order_id}/start", summary="开始维修")
async def start_work_order(
    work_order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    wo = await service.start_work_order(db, work_order_id)
    return success_response(data=WorkOrderResponse.model_validate(wo))


@router.put("/{work_order_id}/complete", summary="提交完成")
async def complete_work_order(
    work_order_id: uuid.UUID,
    data: WorkOrderComplete,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    wo = await service.complete_work_order(db, work_order_id, data)
    return success_response(data=WorkOrderResponse.model_validate(wo))


@router.put("/{work_order_id}/verify", summary="验收")
async def verify_work_order(
    work_order_id: uuid.UUID,
    data: WorkOrderVerify,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    verifier_id = _require_user(current_user)
    wo = await service.verify_work_order(db, work_order_id, verifier_id, data)
    return success_response(data=WorkOrderResponse.model_validate(wo))


@router.put("/{work_order_id}/close", summary="关闭工单")
async def close_work_order(
    work_order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    wo = await service.close_work_order(db, work_order_id)
    return success_response(data=WorkOrderResponse.model_validate(wo))
