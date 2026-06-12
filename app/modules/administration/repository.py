"""Administration data access layer."""

from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.administration.models import ITServiceTicket, Vehicle, VehicleRequest
from app.modules.administration.schemas import (
    ITServiceTicketCreate,
    ITServiceTicketUpdate,
    VehicleCreate,
    VehicleRequestCreate,
    VehicleRequestUpdate,
    VehicleUpdate,
)


class VehicleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(
        self,
        *,
        keyword: str | None = None,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Vehicle], int]:
        stmt = select(Vehicle).where(Vehicle.is_deleted.is_(False))
        count_stmt = select(func.count()).select_from(Vehicle).where(Vehicle.is_deleted.is_(False))

        if keyword:
            like = f"%{keyword}%"
            stmt = stmt.where(Vehicle.plate_number.ilike(like) | Vehicle.brand.ilike(like))
            count_stmt = count_stmt.where(Vehicle.plate_number.ilike(like) | Vehicle.brand.ilike(like))

        if status:
            stmt = stmt.where(Vehicle.status == status)
            count_stmt = count_stmt.where(Vehicle.status == status)

        stmt = stmt.order_by(desc(Vehicle.created_at))
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        result = await self.session.execute(stmt)
        total = await self.session.scalar(count_stmt) or 0
        return list(result.scalars().all()), total

    async def get_by_id(self, vehicle_id: UUID) -> Vehicle | None:
        stmt = select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.is_deleted.is_(False))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, data: VehicleCreate) -> Vehicle:
        vehicle = Vehicle(**data.model_dump(exclude_unset=True))
        self.session.add(vehicle)
        await self.session.flush()
        await self.session.refresh(vehicle)
        return vehicle

    async def update(self, vehicle: Vehicle, data: VehicleUpdate) -> Vehicle:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(vehicle, field, value)
        await self.session.flush()
        await self.session.refresh(vehicle)
        return vehicle

    async def delete(self, vehicle: Vehicle) -> None:
        vehicle.is_deleted = True
        await self.session.flush()


class VehicleRequestRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(
        self,
        *,
        keyword: str | None = None,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[VehicleRequest], int]:
        stmt = select(VehicleRequest).where(VehicleRequest.is_deleted.is_(False))
        count_stmt = select(func.count()).select_from(VehicleRequest).where(VehicleRequest.is_deleted.is_(False))

        if keyword:
            like = f"%{keyword}%"
            stmt = stmt.where(VehicleRequest.applicant_name.ilike(like) | VehicleRequest.purpose.ilike(like))
            count_stmt = count_stmt.where(VehicleRequest.applicant_name.ilike(like) | VehicleRequest.purpose.ilike(like))

        if status:
            stmt = stmt.where(VehicleRequest.status == status)
            count_stmt = count_stmt.where(VehicleRequest.status == status)

        stmt = stmt.order_by(desc(VehicleRequest.created_at))
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        result = await self.session.execute(stmt)
        total = await self.session.scalar(count_stmt) or 0
        return list(result.scalars().all()), total

    async def get_by_id(self, request_id: UUID) -> VehicleRequest | None:
        stmt = select(VehicleRequest).where(VehicleRequest.id == request_id, VehicleRequest.is_deleted.is_(False))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, data: VehicleRequestCreate) -> VehicleRequest:
        request = VehicleRequest(**data.model_dump(exclude_unset=True))
        self.session.add(request)
        await self.session.flush()
        await self.session.refresh(request)
        return request

    async def update(self, request: VehicleRequest, data: VehicleRequestUpdate) -> VehicleRequest:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(request, field, value)
        await self.session.flush()
        await self.session.refresh(request)
        return request

    async def delete(self, request: VehicleRequest) -> None:
        request.is_deleted = True
        await self.session.flush()


class ITServiceTicketRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(
        self,
        *,
        keyword: str | None = None,
        status: str | None = None,
        ticket_type: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ITServiceTicket], int]:
        stmt = select(ITServiceTicket).where(ITServiceTicket.is_deleted.is_(False))
        count_stmt = select(func.count()).select_from(ITServiceTicket).where(ITServiceTicket.is_deleted.is_(False))

        if keyword:
            like = f"%{keyword}%"
            stmt = stmt.where(
                ITServiceTicket.title.ilike(like)
                | ITServiceTicket.requester_name.ilike(like)
                | ITServiceTicket.ticket_no.ilike(like)
            )
            count_stmt = count_stmt.where(
                ITServiceTicket.title.ilike(like)
                | ITServiceTicket.requester_name.ilike(like)
                | ITServiceTicket.ticket_no.ilike(like)
            )

        if status:
            stmt = stmt.where(ITServiceTicket.status == status)
            count_stmt = count_stmt.where(ITServiceTicket.status == status)

        if ticket_type:
            stmt = stmt.where(ITServiceTicket.ticket_type == ticket_type)
            count_stmt = count_stmt.where(ITServiceTicket.ticket_type == ticket_type)

        stmt = stmt.order_by(desc(ITServiceTicket.created_at))
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        result = await self.session.execute(stmt)
        total = await self.session.scalar(count_stmt) or 0
        return list(result.scalars().all()), total

    async def get_by_id(self, ticket_id: UUID) -> ITServiceTicket | None:
        stmt = select(ITServiceTicket).where(ITServiceTicket.id == ticket_id, ITServiceTicket.is_deleted.is_(False))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, data: ITServiceTicketCreate) -> ITServiceTicket:
        ticket = ITServiceTicket(**data.model_dump(exclude_unset=True))
        self.session.add(ticket)
        await self.session.flush()
        await self.session.refresh(ticket)
        return ticket

    async def update(self, ticket: ITServiceTicket, data: ITServiceTicketUpdate) -> ITServiceTicket:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(ticket, field, value)
        await self.session.flush()
        await self.session.refresh(ticket)
        return ticket

    async def delete(self, ticket: ITServiceTicket) -> None:
        ticket.is_deleted = True
        await self.session.flush()
