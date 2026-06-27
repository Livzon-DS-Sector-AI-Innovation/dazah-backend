from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import success_response
from app.modules.warehouse.schemas import (
    PackagingMaterialListResponse,
    PackagingMaterialResponse,
    ProductInventoryListResponse,
    ProductInventoryResponse,
    RawMaterialListResponse,
    RawMaterialResponse,
)
from app.modules.warehouse.service import WarehouseService
from app.shared.module_api import create_module_router
from app.shared.module_registry import MODULES_BY_CODE

router = create_module_router(MODULES_BY_CODE["warehouse"])


def get_warehouse_service(
    session: AsyncSession = Depends(get_db),
) -> WarehouseService:
    return WarehouseService(session)


@router.get(
    "/raw-materials",
    summary="原辅料库存列表",
    response_model=RawMaterialListResponse,
)
async def list_raw_materials(
    service: WarehouseService = Depends(get_warehouse_service),
):
    items = await service.list_raw_materials()
    data = [
        RawMaterialResponse.model_validate(item).model_dump(mode="json")
        for item in items
    ]
    return success_response(data=data)


@router.get(
    "/packaging-materials",
    summary="包材库存列表",
    response_model=PackagingMaterialListResponse,
)
async def list_packaging_materials(
    service: WarehouseService = Depends(get_warehouse_service),
):
    items = await service.list_packaging_materials()
    data = [
        PackagingMaterialResponse.model_validate(item).model_dump(mode="json")
        for item in items
    ]
    return success_response(data=data)


@router.get(
    "/products",
    summary="成品库存列表",
    response_model=ProductInventoryListResponse,
)
async def list_products(
    service: WarehouseService = Depends(get_warehouse_service),
):
    items = await service.list_products()
    data = [
        ProductInventoryResponse.model_validate(item).model_dump(mode="json")
        for item in items
    ]
    return success_response(data=data)
