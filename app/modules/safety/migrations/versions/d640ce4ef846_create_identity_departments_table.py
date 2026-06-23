"""create identity.departments table

Revision ID: d640ce4ef846
Revises: 9a75c1875018
Create Date: 2026-06-18 16:50:53.881605
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd640ce4ef846'
down_revision: Union[str, None] = '9a75c1875018'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── identity.departments ──
    op.execute("CREATE SCHEMA IF NOT EXISTS identity")
    op.create_table('departments',
    sa.Column('feishu_department_id', sa.String(length=64), nullable=False, comment='飞书部门 open_department_id'),
    sa.Column('name', sa.String(length=200), nullable=False, comment='部门名称'),
    sa.Column('parent_feishu_department_id', sa.String(length=64), nullable=True, comment='父部门 ID'),
    sa.Column('leader_user_id', sa.String(length=128), nullable=True, comment='部门主管 user_id'),
    sa.Column('member_count', sa.Integer(), nullable=True, comment='部门成员数'),
    sa.Column('status_is_deleted', sa.Boolean(), nullable=True, comment='飞书侧是否已删除'),
    sa.Column('path', sa.Text(), nullable=True, comment="部门路径 JSON，如 [{'name':'公司','id':'xxx'},...]"),
    sa.Column('order', sa.Integer(), nullable=True, comment='同级排序'),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.Uuid(), nullable=True),
    sa.Column('updated_by', sa.Uuid(), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['identity.users.id'], ),
    sa.ForeignKeyConstraint(['updated_by'], ['identity.users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('feishu_department_id'),
    sa.UniqueConstraint('feishu_department_id', name='uq_identity_departments_feishu_id'),
    schema='identity'
    )


def downgrade() -> None:
    op.drop_table('departments', schema='identity')
