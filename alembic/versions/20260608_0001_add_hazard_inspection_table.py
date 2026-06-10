"""add hazard inspection table

Revision ID: 20260608_0001
Revises: ec4654a030c0
Create Date: 2026-06-08
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260608_0001'
down_revision: Union[str, None] = 'b0cec2530249'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "hazard_inspections",
        # 基础信息
        sa.Column("hazard_number", sa.String(length=32), nullable=False),
        sa.Column("hazard_description", sa.Text(), nullable=False),
        sa.Column("hazard_location", sa.String(length=256), nullable=False),
        sa.Column("hazard_type", sa.String(length=32), nullable=False),
        sa.Column("risk_level", sa.String(length=16), nullable=False),
        # 发现信息
        sa.Column("discoverer", sa.String(length=64), nullable=False),
        sa.Column("discovery_date", sa.Date(), nullable=False),
        # 整改信息
        sa.Column("rectification_person", sa.String(length=64), nullable=True),
        sa.Column("department_head", sa.String(length=64), nullable=True),
        sa.Column("direct_superior", sa.String(length=64), nullable=True),
        sa.Column("approver", sa.String(length=64), nullable=True),
        sa.Column("effect_approver", sa.String(length=64), nullable=True),
        sa.Column("rectification_deadline", sa.Date(), nullable=False),
        sa.Column("rectification_status", sa.String(length=16), nullable=False, server_default="待整改"),
        sa.Column("rectification_measures", sa.Text(), nullable=True),
        sa.Column("corrective_preventive_measures", sa.Text(), nullable=True),
        # 验收信息
        sa.Column("verifier", sa.String(length=64), nullable=True),
        sa.Column("verification_date", sa.Date(), nullable=True),
        # 部门信息
        sa.Column("department", sa.String(length=64), nullable=False),
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
        sa.UniqueConstraint("hazard_number", name="uq_hazard_inspections_hazard_number"),
        sa.ForeignKeyConstraint(["created_by"], ["identity.users.id"]),
        sa.ForeignKeyConstraint(["updated_by"], ["identity.users.id"]),
        schema="safety",
    )

    # 索引
    op.create_index("ix_hazard_inspections_hazard_number", "hazard_inspections", ["hazard_number"], schema="safety")
    op.create_index("ix_hazard_inspections_department", "hazard_inspections", ["department"], schema="safety")
    op.create_index("ix_hazard_inspections_hazard_type", "hazard_inspections", ["hazard_type"], schema="safety")
    op.create_index("ix_hazard_inspections_risk_level", "hazard_inspections", ["risk_level"], schema="safety")
    op.create_index("ix_hazard_inspections_rectification_status", "hazard_inspections", ["rectification_status"], schema="safety")
    op.create_index("ix_hazard_inspections_discovery_date", "hazard_inspections", ["discovery_date"], schema="safety")
    op.create_index("ix_hazard_inspections_rectification_deadline", "hazard_inspections", ["rectification_deadline"], schema="safety")


def downgrade() -> None:
    op.drop_index("ix_hazard_inspections_rectification_deadline", table_name="hazard_inspections", schema="safety")
    op.drop_index("ix_hazard_inspections_discovery_date", table_name="hazard_inspections", schema="safety")
    op.drop_index("ix_hazard_inspections_rectification_status", table_name="hazard_inspections", schema="safety")
    op.drop_index("ix_hazard_inspections_risk_level", table_name="hazard_inspections", schema="safety")
    op.drop_index("ix_hazard_inspections_hazard_type", table_name="hazard_inspections", schema="safety")
    op.drop_index("ix_hazard_inspections_department", table_name="hazard_inspections", schema="safety")
    op.drop_index("ix_hazard_inspections_hazard_number", table_name="hazard_inspections", schema="safety")
    op.drop_table("hazard_inspections", schema="safety")
