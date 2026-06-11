"""add config_type to api_call_configs

Revision ID: d0b8bf6149e6
Revises: 087f572b61f8
Create Date: 2026-06-09 14:10:38.671468
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd0b8bf6149e6'
down_revision: Union[str, None] = '087f572b61f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'api_call_configs',
        sa.Column(
            'config_type',
            sa.String(length=20),
            server_default='text',
            nullable=False,
            comment='配置类型: text(文本模型) / vision(视觉模型)',
        ),
        schema='safety',
    )


def downgrade() -> None:
    op.drop_column('api_call_configs', 'config_type', schema='safety')
