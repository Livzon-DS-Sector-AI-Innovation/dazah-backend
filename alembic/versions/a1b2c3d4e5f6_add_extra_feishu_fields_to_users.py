"""add extra feishu fields to users

Revision ID: a1b2c3d4e5f6
Revises: feeb2a4b3e7d
Create Date: 2026-06-22 17:40:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'feeb2a4b3e7d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('en_name', sa.String(length=100), nullable=True, comment='英文名'), schema='identity')
    op.add_column('users', sa.Column('avatar_thumb', sa.String(length=512), nullable=True, comment='小头像URL'), schema='identity')
    op.add_column('users', sa.Column('avatar_middle', sa.String(length=512), nullable=True, comment='中头像URL'), schema='identity')
    op.add_column('users', sa.Column('avatar_big', sa.String(length=512), nullable=True, comment='大头像URL'), schema='identity')
    op.add_column('users', sa.Column('enterprise_email', sa.String(length=255), nullable=True, comment='企业邮箱'), schema='identity')
    op.add_column('users', sa.Column('tenant_key', sa.String(length=128), nullable=True, comment='租户标识'), schema='identity')


def downgrade() -> None:
    op.drop_column('users', 'tenant_key', schema='identity')
    op.drop_column('users', 'enterprise_email', schema='identity')
    op.drop_column('users', 'avatar_big', schema='identity')
    op.drop_column('users', 'avatar_middle', schema='identity')
    op.drop_column('users', 'avatar_thumb', schema='identity')
    op.drop_column('users', 'en_name', schema='identity')
