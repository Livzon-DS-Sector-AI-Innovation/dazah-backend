"""Administration business workflows live here."""

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.modules.administration.models import ITServiceTicket, Vehicle, VehicleRequest
from app.modules.administration.repository import (
    ITServiceTicketRepository,
    VehicleRepository,
    VehicleRequestRepository,
)
from app.modules.administration.schemas import (
    ITServiceTicketCreate,
    ITServiceTicketUpdate,
    VehicleCreate,
    VehicleRequestCreate,
    VehicleRequestUpdate,
    VehicleUpdate,
)

logger = logging.getLogger(__name__)
_settings = get_settings()


class VehicleService:
    def __init__(self, session: AsyncSession):
        self.repo = VehicleRepository(session)

    async def list_vehicles(
        self,
        *,
        keyword: str | None = None,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ):
        return await self.repo.list(keyword=keyword, status=status, page=page, page_size=page_size)

    async def get_vehicle(self, vehicle_id: UUID) -> Vehicle:
        vehicle = await self.repo.get_by_id(vehicle_id)
        if not vehicle:
            raise ValueError("车辆不存在")
        return vehicle

    async def create_vehicle(self, data: VehicleCreate) -> Vehicle:
        return await self.repo.create(data)

    async def update_vehicle(self, vehicle_id: UUID, data: VehicleUpdate) -> Vehicle:
        vehicle = await self.get_vehicle(vehicle_id)
        return await self.repo.update(vehicle, data)

    async def delete_vehicle(self, vehicle_id: UUID) -> None:
        vehicle = await self.get_vehicle(vehicle_id)
        await self.repo.delete(vehicle)


class VehicleRequestService:
    def __init__(self, session: AsyncSession):
        self.repo = VehicleRequestRepository(session)

    async def list_requests(
        self,
        *,
        keyword: str | None = None,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ):
        return await self.repo.list(keyword=keyword, status=status, page=page, page_size=page_size)

    async def get_request(self, request_id: UUID) -> VehicleRequest:
        request = await self.repo.get_by_id(request_id)
        if not request:
            raise ValueError("用车申请不存在")
        return request

    async def create_request(self, data: VehicleRequestCreate) -> VehicleRequest:
        return await self.repo.create(data)

    async def update_request(self, request_id: UUID, data: VehicleRequestUpdate) -> VehicleRequest:
        request = await self.get_request(request_id)
        return await self.repo.update(request, data)

    async def delete_request(self, request_id: UUID) -> None:
        request = await self.get_request(request_id)
        await self.repo.delete(request)

    async def sync_from_feishu(self) -> dict:
        """从飞书多维表格同步用车申请数据到本地数据库.

        需要在 .env 中配置 FEISHU_BITABLE_APP_TOKEN 和 FEISHU_BITABLE_VEHICLE_REQUEST_TABLE_ID.
        """
        if not _settings.FEISHU_BITABLE_APP_TOKEN or not _settings.FEISHU_BITABLE_VEHICLE_REQUEST_TABLE_ID:
            raise RuntimeError("飞书多维表格未配置，请在 .env 中设置 FEISHU_BITABLE_APP_TOKEN 和 FEISHU_BITABLE_VEHICLE_REQUEST_TABLE_ID")

        try:
            from app.platform.integrations.feishu.bitable import BitableClient

            bitable = BitableClient()
            records = await bitable.search_records(
                _settings.FEISHU_BITABLE_VEHICLE_REQUEST_TABLE_ID,
                page_size=500,
            )

            created = 0
            updated = 0
            failed = 0

            for record in records:
                fields = record.get("fields", {})
                try:
                    # 字段映射（根据实际飞书表格字段名调整）
                    data = VehicleRequestCreate(
                        applicant_name=fields.get("申请人", ""),
                        applicant_department=fields.get("部门", ""),
                        applicant_phone=fields.get("联系电话", ""),
                        purpose=fields.get("用车事由", ""),
                        destination=fields.get("目的地", ""),
                        start_time=datetime.now(),  # 根据实际字段解析
                        end_time=datetime.now(),    # 根据实际字段解析
                        passengers=int(fields.get("乘车人数", 1)),
                        remarks=fields.get("备注", ""),
                    )
                    await self.repo.create(data)
                    created += 1
                except Exception as e:
                    logger.error("同步飞书记录失败: %s", e)
                    failed += 1

            return {
                "created": created,
                "updated": updated,
                "failed": failed,
                "total": len(records),
            }
        except Exception as e:
            logger.error("从飞书同步用车申请失败: %s", e)
            raise


class ITServiceTicketService:
    def __init__(self, session: AsyncSession):
        self.repo = ITServiceTicketRepository(session)

    async def list_tickets(
        self,
        *,
        keyword: str | None = None,
        status: str | None = None,
        ticket_type: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ):
        return await self.repo.list(keyword=keyword, status=status, ticket_type=ticket_type, page=page, page_size=page_size)

    async def get_ticket(self, ticket_id: UUID) -> ITServiceTicket:
        ticket = await self.repo.get_by_id(ticket_id)
        if not ticket:
            raise ValueError("IT工单不存在")
        return ticket

    async def create_ticket(self, data: ITServiceTicketCreate) -> ITServiceTicket:
        return await self.repo.create(data)

    async def update_ticket(self, ticket_id: UUID, data: ITServiceTicketUpdate) -> ITServiceTicket:
        ticket = await self.get_ticket(ticket_id)
        return await self.repo.update(ticket, data)

    async def delete_ticket(self, ticket_id: UUID) -> None:
        ticket = await self.get_ticket(ticket_id)
        await self.repo.delete(ticket)
