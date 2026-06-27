"""Warehouse business workflows live here."""

import hashlib
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.warehouse.models import (
    PackagingMaterialInventory,
    ProductInventory,
    RawMaterialInventory,
)
from app.modules.warehouse.repository import WarehouseRepository


def _safe_number(value: float | int | None) -> float:
    if value is None:
        return 0.0
    return float(value)


def build_warehouse_import_key(*parts: str | None) -> str:
    normalized = "|".join((part or "").strip().lower() for part in parts)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


class WarehouseService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = WarehouseRepository(session)

    async def list_raw_materials(self) -> list[RawMaterialInventory]:
        return await self.repo.list_raw_materials()

    async def list_packaging_materials(self) -> list[PackagingMaterialInventory]:
        return await self.repo.list_packaging_materials()

    async def list_products(self) -> list[ProductInventory]:
        return await self.repo.list_products()

    async def upsert_raw_material_snapshot(
        self,
        *,
        source_id: str | None,
        code: str,
        name: str,
        spec: str | None,
        unit: str | None,
        available: float | int | None,
        safety: float | int | None,
        last_month: float | int | None,
        two_months_ago: float | int | None,
        today_balance: float | int | None,
        front_stock: float | int | None,
        this_month_use: float | int | None,
        warning: str | None,
        product_line: str | None,
        erp_no: str | None,
        delivery: str | None,
        remark: str | None,
        source: str,
    ) -> RawMaterialInventory:
        import_key = build_warehouse_import_key(source_id, code, name, product_line)
        existing = await self.repo.get_raw_material_by_import_key(import_key)
        payload = {
            "source_id": source_id,
            "code": code,
            "name": name,
            "spec": spec,
            "unit": unit,
            "available": _safe_number(available),
            "safety": _safe_number(safety),
            "last_month": _safe_number(last_month),
            "two_months_ago": _safe_number(two_months_ago),
            "today_balance": _safe_number(today_balance),
            "front_stock": _safe_number(front_stock),
            "this_month_use": _safe_number(this_month_use),
            "warning": warning,
            "product_line": product_line,
            "erp_no": erp_no,
            "delivery": delivery,
            "remark": remark,
            "source": source,
            "import_key": import_key,
            "last_synced_at": datetime.now(UTC),
        }
        if existing:
            for field, value in payload.items():
                setattr(existing, field, value)
            existing.is_deleted = False
            await self.repo.session.flush()
            return existing

        item = RawMaterialInventory(**payload)
        return await self.repo.create_raw_material(item)

    async def upsert_packaging_snapshot(
        self,
        *,
        source_id: str | None,
        code: str,
        name: str,
        spec: str | None,
        batch: str | None,
        available: float | int | None,
        safety: float | int | None,
        last_month: float | int | None,
        two_months_ago: float | int | None,
        today_balance: float | int | None,
        front_stock: float | int | None,
        this_month_use: float | int | None,
        warning: str | None,
        product_line: str | None,
        erp_no: str | None,
        delivery: str | None,
        remark: str | None,
        source: str,
    ) -> PackagingMaterialInventory:
        import_key = build_warehouse_import_key(source_id, code, name, product_line)
        existing = await self.repo.get_packaging_material_by_import_key(import_key)
        payload = {
            "source_id": source_id,
            "code": code,
            "name": name,
            "spec": spec,
            "batch": batch,
            "available": _safe_number(available),
            "safety": _safe_number(safety),
            "last_month": _safe_number(last_month),
            "two_months_ago": _safe_number(two_months_ago),
            "today_balance": _safe_number(today_balance),
            "front_stock": _safe_number(front_stock),
            "this_month_use": _safe_number(this_month_use),
            "warning": warning,
            "product_line": product_line,
            "erp_no": erp_no,
            "delivery": delivery,
            "remark": remark,
            "source": source,
            "import_key": import_key,
            "last_synced_at": datetime.now(UTC),
        }
        if existing:
            for field, value in payload.items():
                setattr(existing, field, value)
            existing.is_deleted = False
            await self.repo.session.flush()
            return existing

        item = PackagingMaterialInventory(**payload)
        return await self.repo.create_packaging_material(item)

    async def upsert_product_snapshot(
        self,
        *,
        source_id: str | None,
        name: str,
        spec: str | None,
        order_quantity: float | int | None,
        pending_quantity: float | int | None,
        qualified_quantity: float | int | None,
        subtotal_quantity: float | int | None,
        remaining_quantity: float | int | None,
        unit: str | None,
        remark: str | None,
        source: str,
    ) -> ProductInventory:
        import_key = build_warehouse_import_key(source_id, name, spec, unit)
        existing = await self.repo.get_product_by_import_key(import_key)
        payload = {
            "source_id": source_id,
            "name": name,
            "spec": spec,
            "order_quantity": _safe_number(order_quantity),
            "pending_quantity": _safe_number(pending_quantity),
            "qualified_quantity": _safe_number(qualified_quantity),
            "subtotal_quantity": _safe_number(subtotal_quantity),
            "remaining_quantity": _safe_number(remaining_quantity),
            "unit": unit,
            "remark": remark,
            "source": source,
            "import_key": import_key,
            "last_synced_at": datetime.now(UTC),
        }
        if existing:
            for field, value in payload.items():
                setattr(existing, field, value)
            existing.is_deleted = False
            await self.repo.session.flush()
            return existing

        item = ProductInventory(**payload)
        return await self.repo.create_product(item)
