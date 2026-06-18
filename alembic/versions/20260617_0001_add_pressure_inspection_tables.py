"""add pressure differential inspection tables

Revision ID: 20260617_0001
Revises: 20260615_0001_hr
Create Date: 2026-06-17
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260617_0001'
down_revision: Union[str, None] = '20260615_0001_hr'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ─── point_mappings ───
    op.create_table(
        "point_mappings",
        sa.Column("point_id", sa.String(length=50), nullable=False, comment="位点编号"),
        sa.Column("area", sa.String(length=50), nullable=False, comment="区域"),
        sa.Column("standard_pressure", sa.Integer(), nullable=False, comment="标准压差值(Pa)"),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("point_id", name="uq_point_mappings_point_id"),
        sa.ForeignKeyConstraint(["created_by"], ["identity.users.id"]),
        sa.ForeignKeyConstraint(["updated_by"], ["identity.users.id"]),
        schema="production",
    )
    op.create_index("ix_point_mappings_area", "point_mappings", ["area"], schema="production")

    # ─── pressure_records ───
    op.create_table(
        "pressure_records",
        sa.Column("point_id", sa.String(length=50), nullable=False, comment="位点编号"),
        sa.Column("area", sa.String(length=50), nullable=False, comment="区域"),
        sa.Column("pressure_value", sa.Integer(), nullable=False, comment="压差值(Pa)"),
        sa.Column("standard_pressure", sa.Integer(), nullable=False, comment="标准压差值"),
        sa.Column("record_time", sa.DateTime(timezone=True), nullable=False, comment="记录时间"),
        sa.Column("input_type", sa.String(length=20), nullable=False, server_default="manual", comment="录入方式"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending", comment="审核状态"),
        sa.Column("reject_reason", sa.Text(), nullable=True, comment="驳回原因"),
        sa.Column("image_url", sa.Text(), nullable=True, comment="OCR图片地址"),
        sa.Column("remark", sa.Text(), nullable=True, comment="备注"),
        sa.Column("creator", sa.String(length=255), nullable=True, comment="记录人"),
        sa.Column("batch_id", sa.String(length=36), nullable=True, comment="批次ID"),
        sa.Column("time_slot", sa.String(length=50), nullable=True, comment="时段标签"),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["created_by"], ["identity.users.id"]),
        sa.ForeignKeyConstraint(["updated_by"], ["identity.users.id"]),
        schema="production",
    )
    op.create_index("ix_pressure_records_point_id", "pressure_records", ["point_id"], schema="production")
    op.create_index("ix_pressure_records_area", "pressure_records", ["area"], schema="production")
    op.create_index("ix_pressure_records_record_time", "pressure_records", ["record_time"], schema="production")
    op.create_index("ix_pressure_records_status", "pressure_records", ["status"], schema="production")
    op.create_index("ix_pressure_records_batch_id", "pressure_records", ["batch_id"], schema="production")

    # ─── ocr_tasks ───
    op.create_table(
        "ocr_tasks",
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending", comment="任务状态"),
        sa.Column("image_url", sa.Text(), nullable=False, comment="图片地址"),
        sa.Column("result", sa.JSON(), nullable=True, comment="OCR识别结果"),
        sa.Column("error_message", sa.Text(), nullable=True, comment="错误信息"),
        sa.Column("batch_id", sa.String(length=36), nullable=True, comment="批次ID"),
        sa.Column("creator", sa.String(length=255), nullable=True, comment="创建人"),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["created_by"], ["identity.users.id"]),
        sa.ForeignKeyConstraint(["updated_by"], ["identity.users.id"]),
        schema="production",
    )
    op.create_index("ix_ocr_tasks_status", "ocr_tasks", ["status"], schema="production")

    # ─── data_master ───
    op.create_table(
        "data_master",
        sa.Column("record_date", sa.Date(), nullable=False, comment="记录日期"),
        sa.Column("material_name", sa.String(length=255), nullable=False, comment="物料名称"),
        sa.Column("spec_model", sa.String(length=255), nullable=False, comment="规格型号"),
        sa.Column("quantity", sa.Float(), nullable=False, server_default="0", comment="数量"),
        sa.Column("unit", sa.String(length=50), nullable=False, comment="单位"),
        sa.Column("supplier", sa.String(length=255), nullable=False, comment="供应商"),
        sa.Column("remark", sa.Text(), nullable=True, comment="备注"),
        sa.Column("source", sa.String(length=20), nullable=False, server_default="manual", comment="来源"),
        sa.Column("creator_name", sa.String(length=255), nullable=False, comment="创建人姓名"),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["created_by"], ["identity.users.id"]),
        sa.ForeignKeyConstraint(["updated_by"], ["identity.users.id"]),
        schema="production",
    )
    op.create_index("ix_data_master_record_date", "data_master", ["record_date"], schema="production")
    op.create_index("ix_data_master_material_name", "data_master", ["material_name"], schema="production")
    op.create_index("ix_data_master_source", "data_master", ["source"], schema="production")

    # ─── notifications ───
    op.create_table(
        "notifications",
        sa.Column("type", sa.String(length=50), nullable=False, comment="通知类型"),
        sa.Column("title", sa.String(length=255), nullable=False, comment="标题"),
        sa.Column("message", sa.Text(), nullable=False, comment="消息内容"),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.text("false"), comment="是否已读"),
        sa.Column("target_user_id", sa.String(length=255), nullable=True, comment="目标用户ID"),
        sa.Column("related_id", sa.String(length=36), nullable=True, comment="关联实体ID"),
        sa.Column("related_type", sa.String(length=50), nullable=True, comment="关联实体类型"),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["created_by"], ["identity.users.id"]),
        sa.ForeignKeyConstraint(["updated_by"], ["identity.users.id"]),
        schema="production",
    )
    op.create_index("ix_notifications_is_read", "notifications", ["is_read"], schema="production")
    op.create_index("ix_notifications_target_user_id", "notifications", ["target_user_id"], schema="production")


def downgrade() -> None:
    op.drop_index("ix_notifications_target_user_id", table_name="notifications", schema="production")
    op.drop_index("ix_notifications_is_read", table_name="notifications", schema="production")
    op.drop_table("notifications", schema="production")

    op.drop_index("ix_data_master_source", table_name="data_master", schema="production")
    op.drop_index("ix_data_master_material_name", table_name="data_master", schema="production")
    op.drop_index("ix_data_master_record_date", table_name="data_master", schema="production")
    op.drop_table("data_master", schema="production")

    op.drop_index("ix_ocr_tasks_status", table_name="ocr_tasks", schema="production")
    op.drop_table("ocr_tasks", schema="production")

    op.drop_index("ix_pressure_records_batch_id", table_name="pressure_records", schema="production")
    op.drop_index("ix_pressure_records_status", table_name="pressure_records", schema="production")
    op.drop_index("ix_pressure_records_record_time", table_name="pressure_records", schema="production")
    op.drop_index("ix_pressure_records_area", table_name="pressure_records", schema="production")
    op.drop_index("ix_pressure_records_point_id", table_name="pressure_records", schema="production")
    op.drop_table("pressure_records", schema="production")

    op.drop_index("ix_point_mappings_area", table_name="point_mappings", schema="production")
    op.drop_table("point_mappings", schema="production")
