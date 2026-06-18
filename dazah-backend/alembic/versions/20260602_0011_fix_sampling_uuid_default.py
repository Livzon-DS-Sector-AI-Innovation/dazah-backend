"""fix sampling tables uuid default

Revision ID: 20260602_0011
Revises: 20260602_0010
Create Date: 2026-06-02
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = '20260602_0011'
down_revision: Union[str, None] = '20260602_0010'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Update sampling_orders id column to have UUID default
    op.alter_column(
        "sampling_orders",
        "id",
        existing_type=sa.Uuid(),
        server_default=sa.text("gen_random_uuid()"),
        existing_nullable=False,
        schema="quality",
    )

    # Update sampling_order_items id column to have UUID default
    op.alter_column(
        "sampling_order_items",
        "id",
        existing_type=sa.Uuid(),
        server_default=sa.text("gen_random_uuid()"),
        existing_nullable=False,
        schema="quality",
    )

    # Update sample_retention_ledger id column to have UUID default
    op.alter_column(
        "sample_retention_ledger",
        "id",
        existing_type=sa.Uuid(),
        server_default=sa.text("gen_random_uuid()"),
        existing_nullable=False,
        schema="quality",
    )

    # Update sampling_approval_records id column to have UUID default
    op.alter_column(
        "sampling_approval_records",
        "id",
        existing_type=sa.Uuid(),
        server_default=sa.text("gen_random_uuid()"),
        existing_nullable=False,
        schema="quality",
    )


def downgrade() -> None:
    # Remove UUID defaults
    op.alter_column(
        "sampling_orders",
        "id",
        existing_type=sa.Uuid(),
        server_default=None,
        existing_nullable=False,
        schema="quality",
    )
    op.alter_column(
        "sampling_order_items",
        "id",
        existing_type=sa.Uuid(),
        server_default=None,
        existing_nullable=False,
        schema="quality",
    )
    op.alter_column(
        "sample_retention_ledger",
        "id",
        existing_type=sa.Uuid(),
        server_default=None,
        existing_nullable=False,
        schema="quality",
    )
    op.alter_column(
        "sampling_approval_records",
        "id",
        existing_type=sa.Uuid(),
        server_default=None,
        existing_nullable=False,
        schema="quality",
    )