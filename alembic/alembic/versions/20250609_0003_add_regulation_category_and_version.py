"""add regulation category and version columns

Revision ID: 20250609_0003
Revises: 20250609_0002
Create Date: 2026-06-09 16:30:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20250609_0003'
down_revision: Union[str, None] = '20250609_0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('regulations', sa.Column('category', sa.String(length=32), server_default='其它', nullable=False, comment='类别: 人事, 行政, 其它'), schema='administration')
    op.add_column('regulations', sa.Column('version', sa.String(length=32), nullable=True, comment='版本号'), schema='administration')


def downgrade() -> None:
    op.drop_column('regulations', 'version', schema='administration')
    op.drop_column('regulations', 'category', schema='administration')
