from uuid import UUID

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import paginated_response, success_response
from app.modules.administration.schemas import (
    ITServiceTicketCreate,
    ITServiceTicketResponse,
    ITServiceTicketUpdate,
    VehicleCreate,
    VehicleRequestCreate,
    VehicleRequestResponse,
    VehicleRequestUpdate,
    VehicleResponse,
    VehicleUpdate,
)
from app.modules.administration.service import (
    ITServiceTicketService,
    VehicleRequestService,
    VehicleService,
)
from app.shared.module_api import create_module_router
from app.shared.module_registry import MODULES_BY_CODE
from app.shared.schemas import PageParams

router = create_module_router(MODULES_BY_CODE["administration"])


def get_vehicle_service(session: AsyncSession = Depends(get_db)) -> VehicleService:
    return VehicleService(session)


def get_vehicle_request_service(
    session: AsyncSession = Depends(get_db),
) -> VehicleRequestService:
    return VehicleRequestService(session)


def get_it_ticket_service(
    session: AsyncSession = Depends(get_db),
) -> ITServiceTicketService:
    return ITServiceTicketService(session)


# ─── Vehicle Routes ───

@router.get("/vehicles", summary="车辆列表")
async def list_vehicles(
    keyword: str | None = Query(None, description="车牌号或品牌关键词"),
    status: str | None = Query(None, description="状态筛选"),
    page_params: PageParams = Depends(),
    service: VehicleService = Depends(get_vehicle_service),
):
    vehicles, total = await service.list_vehicles(
        keyword=keyword,
        status=status,
        page=page_params.page,
        page_size=page_params.page_size,
    )
    data = [VehicleResponse.model_validate(v).model_dump(mode="json") for v in vehicles]
    return paginated_response(
        data=data,
        page=page_params.page,
        page_size=page_params.page_size,
        total=total,
    )


@router.post("/vehicles", summary="创建车辆")
async def create_vehicle(
    payload: VehicleCreate,
    service: VehicleService = Depends(get_vehicle_service),
):
    vehicle = await service.create_vehicle(payload)
    return success_response(
        data=VehicleResponse.model_validate(vehicle).model_dump(mode="json"),
        message="车辆创建成功",
        status_code=201,
    )


@router.get("/vehicles/{vehicle_id}", summary="车辆详情")
async def get_vehicle(
    vehicle_id: UUID,
    service: VehicleService = Depends(get_vehicle_service),
):
    vehicle = await service.get_vehicle(vehicle_id)
    return success_response(
        data=VehicleResponse.model_validate(vehicle).model_dump(mode="json"),
    )


@router.put("/vehicles/{vehicle_id}", summary="更新车辆")
async def update_vehicle(
    vehicle_id: UUID,
    payload: VehicleUpdate,
    service: VehicleService = Depends(get_vehicle_service),
):
    vehicle = await service.update_vehicle(vehicle_id, payload)
    return success_response(
        data=VehicleResponse.model_validate(vehicle).model_dump(mode="json"),
        message="车辆更新成功",
    )


@router.delete("/vehicles/{vehicle_id}", summary="删除车辆")
async def delete_vehicle(
    vehicle_id: UUID,
    service: VehicleService = Depends(get_vehicle_service),
):
    await service.delete_vehicle(vehicle_id)
    return success_response(message="车辆删除成功")


# ─── Vehicle Request Routes ───

@router.get("/vehicle-requests", summary="用车申请列表")
async def list_vehicle_requests(
    keyword: str | None = Query(None, description="申请人或事由关键词"),
    status: str | None = Query(None, description="状态筛选"),
    page_params: PageParams = Depends(),
    service: VehicleRequestService = Depends(get_vehicle_request_service),
):
    requests, total = await service.list_requests(
        keyword=keyword,
        status=status,
        page=page_params.page,
        page_size=page_params.page_size,
    )
    data = [VehicleRequestResponse.model_validate(r).model_dump(mode="json") for r in requests]
    return paginated_response(
        data=data,
        page=page_params.page,
        page_size=page_params.page_size,
        total=total,
    )


@router.post("/vehicle-requests", summary="创建用车申请")
async def create_vehicle_request(
    payload: VehicleRequestCreate,
    service: VehicleRequestService = Depends(get_vehicle_request_service),
):
    request = await service.create_request(payload)
    return success_response(
        data=VehicleRequestResponse.model_validate(request).model_dump(mode="json"),
        message="用车申请创建成功",
        status_code=201,
    )


@router.get("/vehicle-requests/{request_id}", summary="用车申请详情")
async def get_vehicle_request(
    request_id: UUID,
    service: VehicleRequestService = Depends(get_vehicle_request_service),
):
    request = await service.get_request(request_id)
    return success_response(
        data=VehicleRequestResponse.model_validate(request).model_dump(mode="json"),
    )


@router.put("/vehicle-requests/{request_id}", summary="更新用车申请")
async def update_vehicle_request(
    request_id: UUID,
    payload: VehicleRequestUpdate,
    service: VehicleRequestService = Depends(get_vehicle_request_service),
):
    request = await service.update_request(request_id, payload)
    return success_response(
        data=VehicleRequestResponse.model_validate(request).model_dump(mode="json"),
        message="用车申请更新成功",
    )


@router.delete("/vehicle-requests/{request_id}", summary="删除用车申请")
async def delete_vehicle_request(
    request_id: UUID,
    service: VehicleRequestService = Depends(get_vehicle_request_service),
):
    await service.delete_request(request_id)
    return success_response(message="用车申请删除成功")


@router.post("/vehicle-requests/sync-from-feishu", summary="从飞书同步用车申请数据")
async def sync_vehicle_requests_from_feishu(
    service: VehicleRequestService = Depends(get_vehicle_request_service),
):
    """从飞书多维表格同步用车申请数据到本地数据库."""
    stats = await service.sync_from_feishu()
    return success_response(
        data=stats,
        message=f"同步完成：新增 {stats['created']} 条，更新 {stats['updated']} 条，失败 {stats['failed']} 条",
    )


# ─── IT Service Ticket Routes ───

@router.get("/it-service-tickets", summary="IT工单列表")
async def list_it_service_tickets(
    keyword: str | None = Query(None, description="标题或报障人关键词"),
    status: str | None = Query(None, description="状态筛选"),
    ticket_type: str | None = Query(None, description="工单类型筛选"),
    page_params: PageParams = Depends(),
    service: ITServiceTicketService = Depends(get_it_ticket_service),
):
    tickets, total = await service.list_tickets(
        keyword=keyword,
        status=status,
        ticket_type=ticket_type,
        page=page_params.page,
        page_size=page_params.page_size,
    )
    data = [ITServiceTicketResponse.model_validate(t).model_dump(mode="json") for t in tickets]
    return paginated_response(
        data=data,
        page=page_params.page,
        page_size=page_params.page_size,
        total=total,
    )


@router.post("/it-service-tickets", summary="创建IT工单")
async def create_it_service_ticket(
    payload: ITServiceTicketCreate,
    service: ITServiceTicketService = Depends(get_it_ticket_service),
):
    ticket = await service.create_ticket(payload)
    return success_response(
        data=ITServiceTicketResponse.model_validate(ticket).model_dump(mode="json"),
        message="IT工单创建成功",
        status_code=201,
    )


@router.get("/it-service-tickets/{ticket_id}", summary="IT工单详情")
async def get_it_service_ticket(
    ticket_id: UUID,
    service: ITServiceTicketService = Depends(get_it_ticket_service),
):
    ticket = await service.get_ticket(ticket_id)
    return success_response(
        data=ITServiceTicketResponse.model_validate(ticket).model_dump(mode="json"),
    )


@router.put("/it-service-tickets/{ticket_id}", summary="更新IT工单")
async def update_it_service_ticket(
    ticket_id: UUID,
    payload: ITServiceTicketUpdate,
    service: ITServiceTicketService = Depends(get_it_ticket_service),
):
    ticket = await service.update_ticket(ticket_id, payload)
    return success_response(
        data=ITServiceTicketResponse.model_validate(ticket).model_dump(mode="json"),
        message="IT工单更新成功",
    )


@router.delete("/it-service-tickets/{ticket_id}", summary="删除IT工单")
async def delete_it_service_ticket(
    ticket_id: UUID,
    service: ITServiceTicketService = Depends(get_it_ticket_service),
):
    await service.delete_ticket(ticket_id)
    return success_response(message="IT工单删除成功")
