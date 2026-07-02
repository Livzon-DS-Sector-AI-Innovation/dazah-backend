"""审计日志表

Revision ID: 20250629_0001
Revises:
Create Date: 2026-06-29

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import BIGINT, SMALLINT, TEXT

# revision identifiers
revision: str = '20250629_0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        't_qs_static_data_audit',
        sa.Column('id', BIGINT(), autoincrement=True, nullable=False),
        sa.Column('module_type', sa.String(50), nullable=False, comment='模块类型'),
        sa.Column('record_id', BIGINT(), nullable=False, comment='被操作记录ID'),
        sa.Column('record_code', sa.String(100), nullable=True, comment='记录编码'),
        sa.Column('operate_type', sa.String(20), nullable=False, comment='操作类型'),
        sa.Column('operate_by', BIGINT(), nullable=False, comment='操作人ID'),
        sa.Column('operate_time', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='操作时间'),
        sa.Column('old_value', TEXT(), nullable=True, comment='变更前内容'),
        sa.Column('new_value', TEXT(), nullable=True, comment='变更后内容'),
        sa.Column('change_summary', sa.String(500), nullable=True, comment='变更摘要'),
        sa.PrimaryKeyConstraint('id'),
        comment='静态数据变更审计日志（不可删除）'
    )
    op.create_index('ix_audit_module_id', 't_qs_static_data_audit', ['module_type', 'record_id'])
    op.create_index('ix_audit_user', 't_qs_static_data_audit', ['operate_by'])
    op.create_index('ix_audit_time', 't_qs_static_data_audit', ['operate_time'])


def downgrade() -> None:
    op.drop_table('t_qs_static_data_audit')