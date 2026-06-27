"""Warehouse request and response schemas live here."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RawMaterialResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source_id: str | None = None
    code: str
    name: str
    spec: str | None = None
    unit: str | None = None
    available: float
    safety: float
    last_month: float
    two_months_ago: float
    today_balance: float
    front_stock: float
    this_month_use: float
    warning: str | None = None
    product_line: str | None = None
    erp_no: str | None = None
    delivery: str | None = None
    remark: str | None = None
    source: str | None = None
    import_key: str
    last_synced_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class PackagingMaterialResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source_id: str | None = None
    code: str
    name: str
    spec: str | None = None
    batch: str | None = None
    available: float
    safety: float
    last_month: float
    two_months_ago: float
    today_balance: float
    front_stock: float
    this_month_use: float
    warning: str | None = None
    product_line: str | None = None
    erp_no: str | None = None
    delivery: str | None = None
    remark: str | None = None
    source: str | None = None
    import_key: str
    last_synced_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ProductInventoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source_id: str | None = None
    name: str
    spec: str | None = None
    order_quantity: float
    pending_quantity: float
    qualified_quantity: float
    subtotal_quantity: float
    remaining_quantity: float
    unit: str | None = None
    remark: str | None = None
    source: str | None = None
    import_key: str
    last_synced_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class RawMaterialListResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: list[RawMaterialResponse]
    meta: dict[str, int] | None = None


class PackagingMaterialListResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: list[PackagingMaterialResponse]
    meta: dict[str, int] | None = None


class ProductInventoryListResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: list[ProductInventoryResponse]
    meta: dict[str, int] | None = None
