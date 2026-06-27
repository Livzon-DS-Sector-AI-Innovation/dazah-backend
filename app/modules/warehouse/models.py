"""Warehouse ORM models live here."""

from datetime import datetime

from sqlalchemy import DateTime, Float, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import BaseModel


class RawMaterialInventory(BaseModel):
    __tablename__ = "raw_material_inventories"
    __table_args__ = (
        Index("ix_warehouse_raw_materials_code", "code"),
        Index("ix_warehouse_raw_materials_product_line", "product_line"),
        Index("ix_warehouse_raw_materials_import_key", "import_key", unique=True),
        {"schema": "warehouse"},
    )

    source_id: Mapped[str | None] = mapped_column(
        String(64), nullable=True, comment="来源记录 ID"
    )
    code: Mapped[str] = mapped_column(String(64), nullable=False, comment="物料编码")
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="物料名称")
    spec: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="规格")
    unit: Mapped[str | None] = mapped_column(String(32), nullable=True, comment="单位")
    available: Mapped[float] = mapped_column(
        Float, nullable=False, default=0, comment="可用库存"
    )
    safety: Mapped[float] = mapped_column(
        Float, nullable=False, default=0, comment="安全库存"
    )
    last_month: Mapped[float] = mapped_column(
        Float, nullable=False, default=0, comment="上月库存/用量"
    )
    two_months_ago: Mapped[float] = mapped_column(
        Float, nullable=False, default=0, comment="前月库存/用量"
    )
    today_balance: Mapped[float] = mapped_column(
        Float, nullable=False, default=0, comment="今日结存"
    )
    front_stock: Mapped[float] = mapped_column(
        Float, nullable=False, default=0, comment="前台库存"
    )
    this_month_use: Mapped[float] = mapped_column(
        Float, nullable=False, default=0, comment="本月用量"
    )
    warning: Mapped[str | None] = mapped_column(
        String(128), nullable=True, comment="预警"
    )
    product_line: Mapped[str | None] = mapped_column(
        String(64), nullable=True, comment="使用产品/类别"
    )
    erp_no: Mapped[str | None] = mapped_column(
        String(128), nullable=True, comment="ERP 编号"
    )
    delivery: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="到货时间"
    )
    remark: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")
    import_key: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="导入唯一键"
    )
    source: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="数据来源"
    )
    last_synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=func.now(),
        comment="最近同步时间",
    )


class PackagingMaterialInventory(BaseModel):
    __tablename__ = "packaging_material_inventories"
    __table_args__ = (
        Index("ix_warehouse_packaging_materials_code", "code"),
        Index("ix_warehouse_packaging_materials_product_line", "product_line"),
        Index(
            "ix_warehouse_packaging_materials_import_key",
            "import_key",
            unique=True,
        ),
        {"schema": "warehouse"},
    )

    source_id: Mapped[str | None] = mapped_column(
        String(64), nullable=True, comment="来源记录 ID"
    )
    code: Mapped[str] = mapped_column(String(64), nullable=False, comment="包材编码")
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="名称")
    spec: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="规格")
    batch: Mapped[str | None] = mapped_column(Text, nullable=True, comment="批次")
    available: Mapped[float] = mapped_column(
        Float, nullable=False, default=0, comment="可用库存"
    )
    safety: Mapped[float] = mapped_column(
        Float, nullable=False, default=0, comment="安全库存"
    )
    last_month: Mapped[float] = mapped_column(
        Float, nullable=False, default=0, comment="上月库存/用量"
    )
    two_months_ago: Mapped[float] = mapped_column(
        Float, nullable=False, default=0, comment="前月库存/用量"
    )
    today_balance: Mapped[float] = mapped_column(
        Float, nullable=False, default=0, comment="今日结存"
    )
    front_stock: Mapped[float] = mapped_column(
        Float, nullable=False, default=0, comment="前台库存"
    )
    this_month_use: Mapped[float] = mapped_column(
        Float, nullable=False, default=0, comment="本月用量"
    )
    warning: Mapped[str | None] = mapped_column(
        String(128), nullable=True, comment="预警"
    )
    product_line: Mapped[str | None] = mapped_column(
        String(64), nullable=True, comment="使用产品"
    )
    erp_no: Mapped[str | None] = mapped_column(
        String(128), nullable=True, comment="ERP 编号"
    )
    delivery: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="到货时间"
    )
    remark: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")
    import_key: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="导入唯一键"
    )
    source: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="数据来源"
    )
    last_synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=func.now(),
        comment="最近同步时间",
    )


class ProductInventory(BaseModel):
    __tablename__ = "product_inventories"
    __table_args__ = (
        Index("ix_warehouse_products_name", "name"),
        Index("ix_warehouse_products_import_key", "import_key", unique=True),
        {"schema": "warehouse"},
    )

    source_id: Mapped[str | None] = mapped_column(
        String(64), nullable=True, comment="来源记录 ID"
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="产品名称")
    spec: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="包装规格"
    )
    order_quantity: Mapped[float] = mapped_column(
        Float, nullable=False, default=0, comment="订单量"
    )
    pending_quantity: Mapped[float] = mapped_column(
        Float, nullable=False, default=0, comment="待检数量"
    )
    qualified_quantity: Mapped[float] = mapped_column(
        Float, nullable=False, default=0, comment="合格数量"
    )
    subtotal_quantity: Mapped[float] = mapped_column(
        Float, nullable=False, default=0, comment="小计"
    )
    remaining_quantity: Mapped[float] = mapped_column(
        Float, nullable=False, default=0, comment="剩余量"
    )
    unit: Mapped[str | None] = mapped_column(String(32), nullable=True, comment="单位")
    remark: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")
    import_key: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="导入唯一键"
    )
    source: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="数据来源"
    )
    last_synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=func.now(),
        comment="最近同步时间",
    )
