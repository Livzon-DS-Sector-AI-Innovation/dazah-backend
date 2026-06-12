"""add regulation file_data column

Revision ID: 20250609_0002
Revises: 20250609_0001
Create Date: 2026-06-09 15:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20250609_0002'
down_revision: Union[str, None] = '20250609_0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('regulations', sa.Column('file_data', sa.Text(), nullable=True, comment='原始文件base64数据'), schema='administration')


def downgrade() -> None:
    op.drop_column('regulations', 'file_data', schema='administration')
