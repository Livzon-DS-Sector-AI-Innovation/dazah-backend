"""add project_id to process_optimizations

Revision ID: 5e2883c65766
Revises: 1242130ddf28
Create Date: 2026-06-24 15:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5e2883c65766'
down_revision = '1242130ddf28'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'process_optimizations',
        sa.Column('project_id', sa.String(50), nullable=True, comment='所属研发项目ID'),
        schema='research'
    )


def downgrade() -> None:
    op.drop_column('process_optimizations', 'project_id', schema='research')
