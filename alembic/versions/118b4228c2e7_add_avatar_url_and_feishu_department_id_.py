"""add avatar_url and feishu_department_id to identity.users

Revision ID: 118b4228c2e7
Revises: ccc4c251c6b4
Create Date: 2026-06-06 09:49:21.009279
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '118b4228c2e7'
down_revision: Union[str, None] = 'ccc4c251c6b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('avatar_url', sa.String(length=512), nullable=True), schema='identity')
    op.add_column('users', sa.Column('feishu_department_id', sa.String(length=64), nullable=True, comment='飞书部门ID'), schema='identity')


def downgrade() -> None:
    op.drop_column('users', 'feishu_department_id', schema='identity')
    op.drop_column('users', 'avatar_url', schema='identity')
