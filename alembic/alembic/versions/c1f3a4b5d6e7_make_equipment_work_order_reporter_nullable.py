"""make equipment work order reporter nullable

Revision ID: c1f3a4b5d6e7
Revises: ba19731e097a
Create Date: 2026-06-30 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c1f3a4b5d6e7"
down_revision: str | None = "ba19731e097a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "work_orders",
        "reporter_id",
        existing_type=sa.Uuid(),
        nullable=True,
        schema="equipment",
    )


def downgrade() -> None:
    op.alter_column(
        "work_orders",
        "reporter_id",
        existing_type=sa.Uuid(),
        nullable=False,
        schema="equipment",
    )
