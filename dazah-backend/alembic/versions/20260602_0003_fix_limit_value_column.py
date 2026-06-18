"""fix limit_value column name in inspection_standard_items

Revision ID: 20260602_0003
Revises: 20260602_0002
Create Date: 2026-06-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260602_0003"
down_revision: str | None = "20260602_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add the missing limit_value column (fix for Chinese column name typo)
    op.add_column(
        "inspection_standard_items",
        sa.Column("limit_value", sa.String(length=255), nullable=True, comment="合格限值"),
        schema="quality"
    )
    # Drop the incorrectly named column if it exists
    op.drop_column("inspection_standard_items", "合格限值", schema="quality")


def downgrade() -> None:
    op.drop_column("inspection_standard_items", "limit_value", schema="quality")