"""Administration module public API for cross-module consumption."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.administration.repository import VehicleRepository, VehicleRequestRepository


async def search_vehicle_requests(
    session: AsyncSession,
    *,
    keyword: str | None = None,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[dict[str, str | int | None]], int]:
    """Search vehicle requests with optional filters."""
    repo = VehicleRequestRepository(session)
    requests, total = await repo.list(
        keyword=keyword, status=status, page=page, page_size=page_size
    )
    data = [
        {
            "id": str(r.id),
            "applicant_name": r.applicant_name,
            "applicant_department": r.applicant_department,
            "applicant_phone": r.applicant_phone,
            "purpose": r.purpose,
            "destination": r.destination,
            "start_time": str(r.start_time) if r.start_time else None,
            "end_time": str(r.end_time) if r.end_time else None,
            "passengers": r.passengers,
            "status": r.status,
            "approver": r.approver,
            "approved_at": str(r.approved_at) if r.approved_at else None,
            "remarks": r.remarks,
            "created_at": str(r.created_at) if r.created_at else None,
        }
        for r in requests
    ]
    return data, total


async def count_vehicle_requests(
    session: AsyncSession,
    *,
    status: str | None = None,
) -> int:
    """Count vehicle requests matching criteria."""
    repo = VehicleRequestRepository(session)
    _, total = await repo.list(status=status, page=1, page_size=1)
    return total


async def search_vehicles(
    session: AsyncSession,
    *,
    keyword: str | None = None,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[dict[str, str | int | None]], int]:
    """Search vehicles with optional filters."""
    repo = VehicleRepository(session)
    vehicles, total = await repo.list(
        keyword=keyword, status=status, page=page, page_size=page_size
    )
    data = [
        {
            "id": str(v.id),
            "plate_number": v.plate_number,
            "brand": v.brand,
            "model": v.model,
            "color": v.color,
            "status": v.status,
            "owner_department": v.owner_department,
            "mileage": v.mileage,
            "purchase_date": str(v.purchase_date) if v.purchase_date else None,
            "remarks": v.remarks,
        }
        for v in vehicles
    ]
    return data, total
