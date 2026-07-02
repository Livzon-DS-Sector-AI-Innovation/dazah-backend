"""Administration data access layer."""

from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.administration.models import GiftInventory, ITServiceTicket, Regulation, Vehicle, VehicleRequest
from app.modules.administration.schemas import (
    GiftInventoryCreate,
    GiftInventoryUpdate,
    GiftRequisitionCreate,
    GiftRequisitionUpdate,
    ITServiceTicketCreate,
    ITServiceTicketUpdate,
    RegulationCreate,
    RegulationUpdate,
    VehicleCreate,
    VehicleRequestCreate,
    VehicleRequestUpdate,
    VehicleUpdate,
)

GIFT_INVENTORY_DB_URL = "postgresql://postgres:postgres@localhost:5432/gift_inventory"



class RegulationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(
        self,
        *,
        keyword: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Regulation], int]:
        from app.modules.administration.models import Regulation
        stmt = select(Regulation).where(Regulation.is_deleted.is_(False))
        count_stmt = select(func.count()).select_from(Regulation).where(Regulation.is_deleted.is_(False))

        if keyword:
            like = f"%{keyword}%"
            stmt = stmt.where(Regulation.title.ilike(like) | Regulation.content.ilike(like))
            count_stmt = count_stmt.where(Regulation.title.ilike(like) | Regulation.content.ilike(like))

        stmt = stmt.order_by(desc(Regulation.created_at))
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        result = await self.session.execute(stmt)
        total = await self.session.scalar(count_stmt) or 0
        return list(result.scalars().all()), total

    async def get_by_id(self, regulation_id: UUID) -> Regulation | None:
        from app.modules.administration.models import Regulation
        stmt = select(Regulation).where(Regulation.id == regulation_id, Regulation.is_deleted.is_(False))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, data: RegulationCreate) -> Regulation:
        from app.modules.administration.models import Regulation
        regulation = Regulation(**data.model_dump(exclude_unset=True))
        self.session.add(regulation)
        await self.session.flush()
        await self.session.refresh(regulation)
        return regulation

    async def update(self, regulation: Regulation, data: RegulationUpdate) -> Regulation:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(regulation, field, value)
        await self.session.flush()
        await self.session.refresh(regulation)
        return regulation

    async def delete(self, regulation: Regulation) -> None:
        regulation.is_deleted = True
        await self.session.flush()


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


class GiftRequisitionRepository:
    """Repository that connects to the standalone gift_inventory database."""

    @staticmethod
    async def _get_conn():
        import asyncpg
        return await asyncpg.connect(GIFT_INVENTORY_DB_URL)

    async def list(
        self,
        *,
        department: str | None = None,
        item_name: str | None = None,
        recipient: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict], int]:
        conn = await self._get_conn()
        try:
            where = []
            args: list = []
            if department:
                args.append(f"%{department}%")
                where.append(f"department ILIKE ${len(args)}")
            if item_name:
                args.append(f"%{item_name}%")
                where.append(f"item_name ILIKE ${len(args)}")
            if recipient:
                args.append(f"%{recipient}%")
                where.append(f"recipient ILIKE ${len(args)}")

            where_clause = " AND ".join(where) if where else "TRUE"

            count_sql = f"SELECT COUNT(*) FROM gift_requisitions WHERE {where_clause}"
            total = await conn.fetchval(count_sql, *args)

            list_sql = f"""
                SELECT id, seq_no, department, item_name, unit_price, quantity,
                       total_amount, recipient, requisition_date, remarks, created_at
                FROM gift_requisitions
                WHERE {where_clause}
                ORDER BY seq_no ASC
                LIMIT ${len(args) + 1} OFFSET ${len(args) + 2}
            """
            args.extend([page_size, (page - 1) * page_size])
            rows = await conn.fetch(list_sql, *args)
            return [dict(r) for r in rows], total or 0
        finally:
            await conn.close()

    async def get_by_id(self, req_id: UUID) -> dict | None:
        conn = await self._get_conn()
        try:
            row = await conn.fetchrow(
                """SELECT id, seq_no, department, item_name, unit_price, quantity,
                          total_amount, recipient, requisition_date, remarks, created_at
                   FROM gift_requisitions WHERE id = $1""",
                req_id,
            )
            return dict(row) if row else None
        finally:
            await conn.close()

    async def create(self, data: GiftRequisitionCreate) -> dict:
        conn = await self._get_conn()
        try:
            payload = data.model_dump(exclude_unset=True)
            columns = list(payload.keys())
            placeholders = [f"${i + 1}" for i in range(len(columns))]
            sql = f"""
                INSERT INTO gift_requisitions ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
                RETURNING id, seq_no, department, item_name, unit_price, quantity,
                          total_amount, recipient, requisition_date, remarks, created_at
            """
            row = await conn.fetchrow(sql, *payload.values())
            return dict(row) if row else {}
        finally:
            await conn.close()

    async def update(self, req_id: UUID, data: GiftRequisitionUpdate) -> dict:
        conn = await self._get_conn()
        try:
            payload = data.model_dump(exclude_unset=True)
            if not payload:
                row = await conn.fetchrow(
                    """SELECT id, seq_no, department, item_name, unit_price, quantity,
                              total_amount, recipient, requisition_date, remarks, created_at
                       FROM gift_requisitions WHERE id = $1""",
                    req_id,
                )
                return dict(row) if row else {}
            sets = [f"{k} = ${i + 2}" for i, k in enumerate(payload.keys())]
            sql = f"""
                UPDATE gift_requisitions
                SET {', '.join(sets)}
                WHERE id = $1
                RETURNING id, seq_no, department, item_name, unit_price, quantity,
                          total_amount, recipient, requisition_date, remarks, created_at
            """
            row = await conn.fetchrow(sql, req_id, *payload.values())
            return dict(row) if row else {}
        finally:
            await conn.close()

    async def delete(self, req_id: UUID) -> None:
        conn = await self._get_conn()
        try:
            await conn.execute("DELETE FROM gift_requisitions WHERE id = $1", req_id)
        finally:
            await conn.close()



class GiftInventoryRepository:
    """Repository that connects to the standalone gift_inventory database."""

    @staticmethod
    async def _get_conn():
        import asyncpg
        return await asyncpg.connect(GIFT_INVENTORY_DB_URL)

    async def list(
        self,
        *,
        keyword: str | None = None,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict], int]:
        conn = await self._get_conn()
        try:
            where = ["is_deleted = FALSE"]
            args: list = []
            if keyword:
                args.append(f"%{keyword}%")
                where.append(f"name ILIKE ${len(args)}")
            if status:
                args.append(status)
                where.append(f"status = ${len(args)}")

            where_clause = " AND ".join(where) if where else "TRUE"

            count_sql = f"SELECT COUNT(*) FROM gift_inventories WHERE {where_clause}"
            total = await conn.fetchval(count_sql, *args)

            list_sql = f"""
                SELECT id, name, specification, unit, opening_stock, incoming_qty,
                       closing_stock, unit_price, total_amount, status, remarks,
                       created_at, updated_at
                FROM gift_inventories
                WHERE {where_clause}
                ORDER BY
                    CASE status
                        WHEN '可用' THEN 1
                        WHEN '库存不足' THEN 2
                        WHEN '停用' THEN 3
                        ELSE 4
                    END,
                    created_at DESC
                LIMIT ${len(args) + 1} OFFSET ${len(args) + 2}
            """
            args.extend([page_size, (page - 1) * page_size])
            rows = await conn.fetch(list_sql, *args)
            return [dict(r) for r in rows], total or 0
        finally:
            await conn.close()

    async def get_by_id(self, inventory_id: UUID) -> dict | None:
        conn = await self._get_conn()
        try:
            row = await conn.fetchrow(
                """SELECT id, name, specification, unit, opening_stock, incoming_qty,
                          closing_stock, unit_price, total_amount, status, remarks,
                          created_at, updated_at
                   FROM gift_inventories WHERE id = $1 AND is_deleted = FALSE""",
                inventory_id,
            )
            return dict(row) if row else None
        finally:
            await conn.close()

    async def create(self, data: GiftInventoryCreate) -> dict:
        conn = await self._get_conn()
        try:
            payload = data.model_dump(exclude_unset=True)
            columns = list(payload.keys())
            placeholders = [f"${i + 1}" for i in range(len(columns))]
            sql = f"""
                INSERT INTO gift_inventories ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
                RETURNING id, name, specification, unit, opening_stock, incoming_qty,
                          closing_stock, unit_price, total_amount, status, remarks,
                          created_at, updated_at
            """
            row = await conn.fetchrow(sql, *payload.values())
            return dict(row) if row else {}
        finally:
            await conn.close()

    async def update(self, inventory_id: UUID, data: GiftInventoryUpdate) -> dict:
        conn = await self._get_conn()
        try:
            payload = data.model_dump(exclude_unset=True)
            if not payload:
                row = await conn.fetchrow(
                    """SELECT id, name, specification, unit, opening_stock, incoming_qty,
                              closing_stock, unit_price, total_amount, status, remarks,
                              created_at, updated_at
                       FROM gift_inventories WHERE id = $1""",
                    inventory_id,
                )
                return dict(row) if row else {}
            sets = [f"{k} = ${i + 2}" for i, k in enumerate(payload.keys())]
            sql = f"""
                UPDATE gift_inventories
                SET {', '.join(sets)}, updated_at = NOW()
                WHERE id = $1
                RETURNING id, name, specification, unit, opening_stock, incoming_qty,
                          closing_stock, unit_price, total_amount, status, remarks,
                          created_at, updated_at
            """
            row = await conn.fetchrow(sql, inventory_id, *payload.values())
            return dict(row) if row else {}
        finally:
            await conn.close()

    async def delete(self, inventory_id: UUID) -> None:
        conn = await self._get_conn()
        try:
            await conn.execute(
                "UPDATE gift_inventories SET is_deleted = TRUE, updated_at = NOW() WHERE id = $1",
                inventory_id,
            )
        finally:
            await conn.close()
