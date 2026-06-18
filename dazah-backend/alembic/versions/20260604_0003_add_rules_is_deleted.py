"""add is_deleted to instrument_calibration_rules

Revision ID: 20260604_0003
Revises: 20260604_0002
Create Date: 2026-06-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260604_0003"
down_revision: str | None = "20260604_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "instrument_calibration_rules",
        sa.Column("is_deleted", sa.Boolean, server_default="false", nullable=False),
        schema="quality"
    )


def downgrade() -> None:
    op.drop_column("instrument_calibration_rules", "is_deleted", schema="quality")
