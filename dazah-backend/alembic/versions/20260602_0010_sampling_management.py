"""sampling management tables

Revision ID: 20260602_0010
Revises: 20260602_0003
Create Date: 2026-06-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260602_0010"
down_revision: str | None = "20260602_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ========== Sampling Orders (取样单主表) ==========
    op.create_table(
        "sampling_orders",
        sa.Column("order_no", sa.String(length=64), nullable=False, comment="取样单号"),
        sa.Column("source_type", sa.String(length=32), nullable=False, comment="来源类型：purchase_inbound生产批号"),
        sa.Column("source_no", sa.String(length=64), nullable=True, comment="关联单号（来料入库单号/生产批号）"),
        sa.Column("material_code", sa.String(length=64), nullable=False, comment="物料编码"),
        sa.Column("material_name", sa.String(length=255), nullable=True, comment="物料名称"),
        sa.Column("material_category", sa.String(length=32), nullable=True, comment="物料类别"),
        sa.Column("batch_no", sa.String(length=64), nullable=True, comment="批次号"),
        sa.Column("specification", sa.String(length=128), nullable=True, comment="规格"),
        sa.Column("unit", sa.String(length=32), nullable=True, comment="单位"),
        sa.Column("quantity", sa.Numeric(precision=18, scale=6), nullable=True, comment="批量/数量"),
        sa.Column("sampling_source", sa.String(length=32), nullable=False, comment="取样来源：purchased_material车间中间体、finished_product"),
        sa.Column("sampling_quantity", sa.Numeric(precision=18, scale=6), nullable=True, comment="取样量"),
        sa.Column("sampling_location", sa.String(length=255), nullable=True, comment="取样地点"),
        sa.Column("sampling_date", sa.DateTime(timezone=True), nullable=True, comment="取样日期"),
        sa.Column("sampler_id", sa.Uuid(), nullable=True, comment="取样人ID"),
        sa.Column("sampler_name", sa.String(length=100), nullable=True, comment="取样人姓名"),
        sa.Column("status", sa.String(length=32), server_default=sa.text("'draft'"), nullable=False, comment="状态：draft驳回approved、effective"),
        sa.Column("sampling_result", sa.String(length=32), nullable=True, comment="取样判定：normal异常"),
        sa.Column("exception_reasons", sa.Text(), nullable=True, comment="异常原因（JSON数组）"),
        sa.Column("deviation_id", sa.Uuid(), nullable=True, comment="关联偏差ID"),
        sa.Column("remark", sa.Text(), nullable=True, comment="备注"),
        sa.Column("id", sa.Uuid(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["sampler_id"], ["identity.users.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["identity.users.id"]),
        sa.ForeignKeyConstraint(["updated_by"], ["identity.users.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="quality",
    )
    op.create_index("idx_sampling_order_no", "sampling_orders", ["order_no"], unique=True, schema="quality")
    op.create_index("idx_sampling_source_no", "sampling_orders", ["source_no"], unique=False, schema="quality")
    op.create_index("idx_sampling_material_code", "sampling_orders", ["material_code"], unique=False, schema="quality")
    op.create_index("idx_sampling_status", "sampling_orders", ["status"], unique=False, schema="quality")
    op.create_index("idx_sampling_source", "sampling_orders", ["sampling_source"], unique=False, schema="quality")
    op.create_index("idx_sampling_date", "sampling_orders", ["sampling_date"], unique=False, schema="quality")

    # ========== Sampling Order Items (取样明细表) ==========
    op.create_table(
        "sampling_order_items",
        sa.Column("sampling_order_id", sa.Uuid(), nullable=False, comment="取样单ID"),
        sa.Column("item_no", sa.Integer(), nullable=False, comment="项次"),
        sa.Column("sample_no", sa.String(length=64), nullable=False, comment="样品编号"),
        sa.Column("sampling_count", sa.Integer(), nullable=True, comment="取样份数"),
        sa.Column("retention_count", sa.Integer(), nullable=True, comment="留样份数"),
        sa.Column("retention_location", sa.String(length=255), nullable=True, comment="留样存放位置"),
        sa.Column("sample_status", sa.String(length=32), nullable=True, comment="样品状态：pending已留样已使用、expired"),
        sa.Column("retention_date", sa.DateTime(timezone=True), nullable=True, comment="留样日期"),
        sa.Column("expiry_date", sa.DateTime(timezone=True), nullable=True, comment="留样有效期"),
        sa.Column("is_expired", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="是否到期"),
        sa.Column("disposal_date", sa.DateTime(timezone=True), nullable=True, comment="处置日期"),
        sa.Column("disposal_method", sa.String(length=64), nullable=True, comment="处置方式"),
        sa.Column("remark", sa.Text(), nullable=True, comment="备注"),
        sa.Column("id", sa.Uuid(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["sampling_order_id"], ["quality.sampling_orders.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["identity.users.id"]),
        sa.ForeignKeyConstraint(["updated_by"], ["identity.users.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="quality",
    )
    op.create_index("idx_sampling_items_order_id", "sampling_order_items", ["sampling_order_id"], unique=False, schema="quality")
    op.create_index("idx_sampling_items_sample_no", "sampling_order_items", ["sample_no"], unique=True, schema="quality")

    # ========== Sample Retention Ledger (留样台账表) ==========
    op.create_table(
        "sample_retention_ledger",
        sa.Column("sampling_item_id", sa.Uuid(), nullable=False, comment="取样明细ID"),
        sa.Column("sampling_order_id", sa.Uuid(), nullable=False, comment="取样单ID"),
        sa.Column("order_no", sa.String(length=64), nullable=False, comment="取样单号"),
        sa.Column("sample_no", sa.String(length=64), nullable=False, comment="样品编号"),
        sa.Column("material_code", sa.String(length=64), nullable=False, comment="物料编码"),
        sa.Column("material_name", sa.String(length=255), nullable=True, comment="物料名称"),
        sa.Column("batch_no", sa.String(length=64), nullable=True, comment="批次号"),
        sa.Column("retention_count", sa.Integer(), nullable=True, comment="留样份数"),
        sa.Column("retention_location", sa.String(length=255), nullable=True, comment="存放位置"),
        sa.Column("retention_date", sa.DateTime(timezone=True), nullable=True, comment="留样日期"),
        sa.Column("expiry_date", sa.DateTime(timezone=True), nullable=True, comment="有效期"),
        sa.Column("retention_status", sa.String(length=32), nullable=False, comment="状态：retained已到期、disposed"),
        sa.Column("disposal_date", sa.DateTime(timezone=True), nullable=True, comment="处置日期"),
        sa.Column("disposal_method", sa.String(length=64), nullable=True, comment="处置方式"),
        sa.Column("disposal_remark", sa.Text(), nullable=True, comment="处置备注"),
        sa.Column("reminder_sent", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="是否已发送提醒"),
        sa.Column("remark", sa.Text(), nullable=True, comment="备注"),
        sa.Column("id", sa.Uuid(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["sampling_item_id"], ["quality.sampling_order_items.id"]),
        sa.ForeignKeyConstraint(["sampling_order_id"], ["quality.sampling_orders.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["identity.users.id"]),
        sa.ForeignKeyConstraint(["updated_by"], ["identity.users.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="quality",
    )
    op.create_index("idx_retention_sampling_order_id", "sample_retention_ledger", ["sampling_order_id"], unique=False, schema="quality")
    op.create_index("idx_retention_sample_no", "sample_retention_ledger", ["sample_no"], unique=True, schema="quality")
    op.create_index("idx_retention_material_code", "sample_retention_ledger", ["material_code"], unique=False, schema="quality")
    op.create_index("idx_retention_expiry_date", "sample_retention_ledger", ["expiry_date"], unique=False, schema="quality")
    op.create_index("idx_retention_status", "sample_retention_ledger", ["retention_status"], unique=False, schema="quality")

    # ========== Sampling Approval Records (取样审批记录) ==========
    op.create_table(
        "sampling_approval_records",
        sa.Column("sampling_order_id", sa.Uuid(), nullable=False, comment="取样单ID"),
        sa.Column("approval_level", sa.Integer(), nullable=False, comment="审批级别：1仓储/生产、2QA"),
        sa.Column("approval_status", sa.String(length=32), nullable=False, comment="审批状态：pendingapprovedrejected"),
        sa.Column("approver_role", sa.String(length=64), nullable=True, comment="审批角色"),
        sa.Column("approver_id", sa.Uuid(), nullable=True, comment="审批人ID"),
        sa.Column("approver_name", sa.String(length=100), nullable=True, comment="审批人姓名"),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True, comment="审批时间"),
        sa.Column("comments", sa.Text(), nullable=True, comment="审批意见"),
        sa.Column("id", sa.Uuid(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["sampling_order_id"], ["quality.sampling_orders.id"]),
        sa.ForeignKeyConstraint(["approver_id"], ["identity.users.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["identity.users.id"]),
        sa.ForeignKeyConstraint(["updated_by"], ["identity.users.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="quality",
    )
    op.create_index("idx_sampling_approval_order_id", "sampling_approval_records", ["sampling_order_id"], unique=False, schema="quality")


def downgrade() -> None:
    op.drop_table("sampling_approval_records", schema="quality")
    op.drop_table("sample_retention_ledger", schema="quality")
    op.drop_table("sampling_order_items", schema="quality")
    op.drop_table("sampling_orders", schema="quality")
