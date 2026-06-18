"""add input_qty to batches table

Revision ID: 20260602_0001
Revises: 20260601_0001
Create Date: 2026-06-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260602_0001"
down_revision: str | None = "20260601_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 添加 input_qty 字段到 batches 表
    op.add_column(
        "batches",
        sa.Column("input_qty", sa.Float(), nullable=True, comment="实际投入数量"),
        schema="production"
    )


def downgrade() -> None:
    op.drop_column("batches", "input_qty", schema="production")