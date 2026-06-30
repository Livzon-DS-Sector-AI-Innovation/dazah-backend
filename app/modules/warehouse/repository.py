"""Warehouse database queries live here."""

from uuid import UUID

from sqlalchemy import asc, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.warehouse.models import (
    PackagingMaterialInventory,
    ProductInventory,
    RawMaterialInventory,
    WarehouseFeishuConfig,
    WarehouseFeishuField,
    WarehouseFeishuRecord,
    WarehouseFeishuTable,
)


class WarehouseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_raw_materials(self) -> list[RawMaterialInventory]:
        result = await self.session.execute(
            select(RawMaterialInventory)
            .where(RawMaterialInventory.is_deleted.is_(False))
            .order_by(
                asc(RawMaterialInventory.product_line),
                asc(RawMaterialInventory.code),
                asc(RawMaterialInventory.name),
            )
        )
        return list(result.scalars().all())

    async def list_packaging_materials(self) -> list[PackagingMaterialInventory]:
        result = await self.session.execute(
            select(PackagingMaterialInventory)
            .where(PackagingMaterialInventory.is_deleted.is_(False))
            .order_by(
                asc(PackagingMaterialInventory.product_line),
                asc(PackagingMaterialInventory.code),
                asc(PackagingMaterialInventory.name),
            )
        )
        return list(result.scalars().all())

    async def list_products(self) -> list[ProductInventory]:
        result = await self.session.execute(
            select(ProductInventory)
            .where(ProductInventory.is_deleted.is_(False))
            .order_by(
                asc(ProductInventory.name),
                asc(ProductInventory.spec),
            )
        )
        return list(result.scalars().all())

    async def get_raw_material_by_import_key(
        self, import_key: str
    ) -> RawMaterialInventory | None:
        result = await self.session.execute(
            select(RawMaterialInventory).where(
                RawMaterialInventory.import_key == import_key
            )
        )
        return result.scalar_one_or_none()

    async def get_packaging_material_by_import_key(
        self, import_key: str
    ) -> PackagingMaterialInventory | None:
        result = await self.session.execute(
            select(PackagingMaterialInventory).where(
                PackagingMaterialInventory.import_key == import_key
            )
        )
        return result.scalar_one_or_none()

    async def get_product_by_import_key(
        self, import_key: str
    ) -> ProductInventory | None:
        result = await self.session.execute(
            select(ProductInventory).where(ProductInventory.import_key == import_key)
        )
        return result.scalar_one_or_none()

    async def create_raw_material(
        self, item: RawMaterialInventory
    ) -> RawMaterialInventory:
        self.session.add(item)
        await self.session.flush()
        return item

    async def create_packaging_material(
        self, item: PackagingMaterialInventory
    ) -> PackagingMaterialInventory:
        self.session.add(item)
        await self.session.flush()
        return item

    async def create_product(self, item: ProductInventory) -> ProductInventory:
        self.session.add(item)
        await self.session.flush()
        return item

    async def get_active_feishu_config(self) -> WarehouseFeishuConfig | None:
        result = await self.session.execute(
            select(WarehouseFeishuConfig)
            .where(
                WarehouseFeishuConfig.is_deleted.is_(False),
                WarehouseFeishuConfig.is_active.is_(True),
            )
            .order_by(WarehouseFeishuConfig.updated_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_any_feishu_config(self) -> WarehouseFeishuConfig | None:
        result = await self.session.execute(
            select(WarehouseFeishuConfig)
            .where(WarehouseFeishuConfig.is_deleted.is_(False))
            .order_by(WarehouseFeishuConfig.updated_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def save_feishu_config(
        self, config: WarehouseFeishuConfig
    ) -> WarehouseFeishuConfig:
        self.session.add(config)
        await self.session.flush()
        return config

    async def list_feishu_tables(
        self,
        *,
        business_domain: str | None = None,
        keyword: str | None = None,
        enabled: bool | None = None,
    ) -> list[WarehouseFeishuTable]:
        conditions = [WarehouseFeishuTable.is_deleted.is_(False)]
        if business_domain:
            conditions.append(WarehouseFeishuTable.business_domain == business_domain)
        if enabled is not None:
            conditions.append(WarehouseFeishuTable.is_enabled.is_(enabled))
        if keyword:
            pattern = f"%{keyword.strip()}%"
            conditions.append(
                or_(
                    WarehouseFeishuTable.name.ilike(pattern),
                    WarehouseFeishuTable.table_id.ilike(pattern),
                    WarehouseFeishuTable.app_token.ilike(pattern),
                )
            )
        result = await self.session.execute(
            select(WarehouseFeishuTable)
            .where(*conditions)
            .order_by(
                asc(WarehouseFeishuTable.business_domain),
                asc(WarehouseFeishuTable.name),
                asc(WarehouseFeishuTable.table_id),
            )
        )
        return list(result.scalars().all())

    async def get_feishu_table(
        self, business_domain: str, app_token: str, table_id: str
    ) -> WarehouseFeishuTable | None:
        result = await self.session.execute(
            select(WarehouseFeishuTable).where(
                WarehouseFeishuTable.is_deleted.is_(False),
                WarehouseFeishuTable.business_domain == business_domain,
                WarehouseFeishuTable.app_token == app_token,
                WarehouseFeishuTable.table_id == table_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_feishu_table_by_id(
        self, table_pk: UUID
    ) -> WarehouseFeishuTable | None:
        result = await self.session.execute(
            select(WarehouseFeishuTable).where(
                WarehouseFeishuTable.is_deleted.is_(False),
                WarehouseFeishuTable.id == table_pk,
            )
        )
        return result.scalar_one_or_none()

    async def get_enabled_feishu_table(
        self, app_token: str, table_id: str
    ) -> WarehouseFeishuTable | None:
        result = await self.session.execute(
            select(WarehouseFeishuTable).where(
                WarehouseFeishuTable.is_deleted.is_(False),
                WarehouseFeishuTable.is_enabled.is_(True),
                WarehouseFeishuTable.app_token == app_token,
                WarehouseFeishuTable.table_id == table_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_enabled_feishu_tables(self) -> list[WarehouseFeishuTable]:
        result = await self.session.execute(
            select(WarehouseFeishuTable)
            .where(
                WarehouseFeishuTable.is_deleted.is_(False),
                WarehouseFeishuTable.is_enabled.is_(True),
            )
            .order_by(
                asc(WarehouseFeishuTable.business_domain),
                asc(WarehouseFeishuTable.name),
            )
        )
        return list(result.scalars().all())

    async def save_feishu_table(
        self, table: WarehouseFeishuTable
    ) -> WarehouseFeishuTable:
        self.session.add(table)
        await self.session.flush()
        return table

    async def get_feishu_field(
        self, business_domain: str, app_token: str, table_id: str, field_id: str
    ) -> WarehouseFeishuField | None:
        result = await self.session.execute(
            select(WarehouseFeishuField).where(
                WarehouseFeishuField.is_deleted.is_(False),
                WarehouseFeishuField.business_domain == business_domain,
                WarehouseFeishuField.app_token == app_token,
                WarehouseFeishuField.table_id == table_id,
                WarehouseFeishuField.field_id == field_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_feishu_fields(
        self, business_domain: str, app_token: str, table_id: str
    ) -> list[WarehouseFeishuField]:
        result = await self.session.execute(
            select(WarehouseFeishuField)
            .where(
                WarehouseFeishuField.is_deleted.is_(False),
                WarehouseFeishuField.business_domain == business_domain,
                WarehouseFeishuField.app_token == app_token,
                WarehouseFeishuField.table_id == table_id,
            )
            .order_by(
                asc(WarehouseFeishuField.created_at),
                asc(WarehouseFeishuField.field_name),
            )
        )
        return list(result.scalars().all())

    async def save_feishu_field(
        self, field: WarehouseFeishuField
    ) -> WarehouseFeishuField:
        self.session.add(field)
        await self.session.flush()
        return field

    async def get_feishu_record(
        self, business_domain: str, app_token: str, table_id: str, record_id: str
    ) -> WarehouseFeishuRecord | None:
        result = await self.session.execute(
            select(WarehouseFeishuRecord).where(
                WarehouseFeishuRecord.business_domain == business_domain,
                WarehouseFeishuRecord.app_token == app_token,
                WarehouseFeishuRecord.table_id == table_id,
                WarehouseFeishuRecord.record_id == record_id,
            )
        )
        return result.scalar_one_or_none()

    async def save_feishu_record(
        self, record: WarehouseFeishuRecord
    ) -> WarehouseFeishuRecord:
        self.session.add(record)
        await self.session.flush()
        return record

    async def mark_missing_feishu_records_deleted(
        self,
        *,
        business_domain: str,
        app_token: str,
        table_id: str,
        active_record_ids: set[str],
    ) -> None:
        stmt = (
            update(WarehouseFeishuRecord)
            .where(
                WarehouseFeishuRecord.business_domain == business_domain,
                WarehouseFeishuRecord.app_token == app_token,
                WarehouseFeishuRecord.table_id == table_id,
                WarehouseFeishuRecord.is_deleted.is_(False),
                WarehouseFeishuRecord.record_id.not_in(active_record_ids),
            )
            .values(is_deleted=True)
        )
        await self.session.execute(stmt)

    async def list_feishu_records(
        self,
        *,
        business_domain: str,
        app_token: str,
        table_id: str,
        keyword: str | None,
        field: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[WarehouseFeishuRecord], int]:
        conditions = [
            WarehouseFeishuRecord.is_deleted.is_(False),
            WarehouseFeishuRecord.business_domain == business_domain,
            WarehouseFeishuRecord.app_token == app_token,
            WarehouseFeishuRecord.table_id == table_id,
        ]
        if keyword:
            pattern = f"%{keyword.strip()}%"
            if field:
                conditions.append(
                    WarehouseFeishuRecord.fields[field].astext.ilike(pattern)
                )
            else:
                conditions.append(WarehouseFeishuRecord.search_text.ilike(pattern))

        total_result = await self.session.execute(
            select(func.count()).select_from(WarehouseFeishuRecord).where(*conditions)
        )
        total = int(total_result.scalar_one() or 0)

        result = await self.session.execute(
            select(WarehouseFeishuRecord)
            .where(*conditions)
            .order_by(
                WarehouseFeishuRecord.feishu_last_modified_time.desc().nullslast(),
                WarehouseFeishuRecord.updated_at.desc(),
            )
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total
