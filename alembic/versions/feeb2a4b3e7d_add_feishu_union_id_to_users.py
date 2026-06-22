"""add feishu_union_id to users

Revision ID: feeb2a4b3e7d
Revises: d4e8f2a9b3c5
Create Date: 2026-06-22 17:23:00.781769
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'feeb2a4b3e7d'
down_revision: Union[str, None] = 'd4e8f2a9b3c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('feishu_union_id', sa.String(length=128), nullable=True), schema='identity')


def downgrade() -> None:
    op.drop_column('users', 'feishu_union_id', schema='identity')
