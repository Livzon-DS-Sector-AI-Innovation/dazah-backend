"""add_vehicle_photo_fields

Revision ID: f433f7bcd8f9
Revises: 096ff697eef8
Create Date: 2026-06-10 14:49:57.016732
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f433f7bcd8f9'
down_revision: Union[str, None] = '096ff697eef8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('vehicles', sa.Column('photo_data', sa.Text(), nullable=True, comment='车辆照片base64数据'), schema='administration')
    op.add_column('vehicles', sa.Column('photo_type', sa.String(128), nullable=True, comment='照片MIME类型'), schema='administration')


def downgrade() -> None:
    op.drop_column('vehicles', 'photo_data', schema='administration')
    op.drop_column('vehicles', 'photo_type', schema='administration')
