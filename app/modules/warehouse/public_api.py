"""Warehouse module public API — cross-module access points.

Other modules should import from this file instead of directly accessing
internal service/repository/models.
"""

from app.modules.warehouse.service import WarehouseService
from app.modules.warehouse.repository import WarehouseRepository
from app.modules.warehouse.schemas import (
    RawMaterialResponse,
    PackagingMaterialResponse,
    ProductInventoryResponse,
)

__all__ = [
    "WarehouseService",
    "WarehouseRepository",
    "RawMaterialResponse",
    "PackagingMaterialResponse",
    "ProductInventoryResponse",
]
