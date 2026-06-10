"""add label verification table

Revision ID: 20260610_0001
Revises: 20260608_0001
Create Date: 2026-06-10
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260610_0001'
down_revision: Union[str, None] = '20260608_0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "label_verifications",
        # 基础信息
        sa.Column("batch_number", sa.String(length=32), nullable=False),
        sa.Column("product_name", sa.String(length=128), nullable=False),
        sa.Column("production_date", sa.Date(), nullable=False),
        sa.Column("expiry_date", sa.Date(), nullable=False),
        # 桶数与重量信息
        sa.Column("total_barrels", sa.Integer(), nullable=False),
        sa.Column("standard_barrels", sa.Integer(), nullable=False),
        sa.Column("remainder_barrel", sa.Integer(), nullable=False),
        sa.Column("standard_weight", sa.Float(), nullable=False),
        sa.Column("remainder_weight", sa.Float(), nullable=False),
        sa.Column("total_weight", sa.Float(), nullable=False),
        # 8项结论状态
        sa.Column("check_batch_number", sa.Boolean(), nullable=False),
        sa.Column("check_production_date", sa.Boolean(), nullable=False),
        sa.Column("check_expiry_date", sa.Boolean(), nullable=False),
        sa.Column("check_standard_barrels", sa.Boolean(), nullable=False),
        sa.Column("check_remainder_barrel", sa.Boolean(), nullable=False),
        sa.Column("check_total_weight", sa.Boolean(), nullable=False),
        sa.Column("check_all_barrels_identified", sa.Boolean(), nullable=False),
        sa.Column("check_exception_handled", sa.Boolean(), nullable=False),
        # 总体结论
        sa.Column("result_status", sa.String(length=16), nullable=False, server_default="全部一致"),
        sa.Column("result_summary", sa.Text(), nullable=False),
        # 视频来源信息
        sa.Column("video_file_key", sa.String(length=256), nullable=False),
        sa.Column("video_file_name", sa.String(length=256), nullable=True),
        sa.Column("video_frame_count", sa.Integer(), nullable=True),
        sa.Column("video_fps", sa.Float(), nullable=True),
        # 复核时间
        sa.Column("verification_date", sa.Date(), nullable=False),
        sa.Column("verification_time", sa.DateTime(timezone=True), nullable=False),
        # 备注
        sa.Column("remarks", sa.Text(), nullable=True),
        # BaseModel 标准字段
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        # 约束
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["created_by"], ["identity.users.id"]),
        sa.ForeignKeyConstraint(["updated_by"], ["identity.users.id"]),
        schema="quality",
    )

    # 索引
    op.create_index("ix_label_verifications_batch_number", "label_verifications", ["batch_number"], schema="quality")
    op.create_index("ix_label_verifications_production_date", "label_verifications", ["production_date"], schema="quality")
    op.create_index("ix_label_verifications_verification_date", "label_verifications", ["verification_date"], schema="quality")
    op.create_index("ix_label_verifications_result_status", "label_verifications", ["result_status"], schema="quality")


def downgrade() -> None:
    op.drop_index("ix_label_verifications_result_status", table_name="label_verifications", schema="quality")
    op.drop_index("ix_label_verifications_verification_date", table_name="label_verifications", schema="quality")
    op.drop_index("ix_label_verifications_production_date", table_name="label_verifications", schema="quality")
    op.drop_index("ix_label_verifications_batch_number", table_name="label_verifications", schema="quality")
    op.drop_table("label_verifications", schema="quality")
