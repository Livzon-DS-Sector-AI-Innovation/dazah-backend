"""Add sop_ai_config is_deleted, is_enabled, sort_order

Revision ID: 20260626_0002
Revises: 20260626_0001
Create Date: 2026-06-26 14:40:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '20260626_0002'
down_revision = 'sop_ai_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add is_deleted, is_enabled, sort_order columns to sop_ai_config"""
    op.add_column(
        'sop_ai_config',
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false')
    )
    op.add_column(
        'sop_ai_config',
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default='true')
    )
    op.add_column(
        'sop_ai_config',
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0')
    )


def downgrade() -> None:
    """Remove added columns"""
    op.drop_column('sop_ai_config', 'sort_order')
    op.drop_column('sop_ai_config', 'is_enabled')
    op.drop_column('sop_ai_config', 'is_deleted')