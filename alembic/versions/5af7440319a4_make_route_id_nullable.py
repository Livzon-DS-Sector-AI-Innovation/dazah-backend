"""make_route_id_nullable

Revision ID: 5af7440319a4
Revises: 5e2883c65766
Create Date: 2026-06-24 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5af7440319a4'
down_revision = '5e2883c65766'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        'process_optimizations',
        'route_id',
        existing_type=sa.String(50),
        nullable=True,
        schema='research'
    )


def downgrade() -> None:
    op.alter_column(
        'process_optimizations',
        'route_id',
        existing_type=sa.String(50),
        nullable=False,
        schema='research'
    )
