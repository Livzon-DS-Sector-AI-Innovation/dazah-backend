"""add scheduled_tasks and scheduled_task_logs tables

Revision ID: 20260615_0001
Revises: f1a2b3c4d5e6
Create Date: 2026-06-15 10:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260615_0001'
down_revision: Union[str, None] = 'f1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'scheduled_tasks',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False, comment='任务名称'),
        sa.Column('description', sa.Text(), nullable=True, comment='任务描述'),
        sa.Column('cron_expression', sa.String(100), nullable=False, comment='Cron 表达式'),
        sa.Column('cron_desc', sa.String(200), nullable=True, comment='Cron 可读描述'),
        sa.Column('feishu_chat_id', sa.String(100), nullable=False, comment='目标飞书群聊 chat_id'),
        sa.Column('feishu_chat_name', sa.String(200), nullable=True, comment='飞书群聊名称快照'),
        sa.Column('header_color', sa.String(20), nullable=False, server_default='blue', comment='卡片头部颜色'),
        sa.Column('data_sources', sa.JSON(), nullable=True, comment='数据来源配置'),
        sa.Column('card_template', sa.Text(), nullable=True, comment='消息卡片模板'),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default='true', comment='是否启用'),
        sa.Column('last_run_at', sa.DateTime(timezone=True), nullable=True, comment='上次执行时间'),
        sa.Column('last_run_status', sa.String(20), nullable=True, comment='上次执行状态'),
        sa.Column('last_error', sa.Text(), nullable=True, comment='上次错误信息'),
        sa.Column('next_run_at', sa.DateTime(timezone=True), nullable=True, comment='下次执行时间'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='uq_scheduled_tasks_name'),
        schema='safety',
    )
    op.create_index('ix_scheduled_tasks_enabled_next', 'scheduled_tasks', ['is_enabled', 'next_run_at'], schema='safety')

    op.create_table(
        'scheduled_task_logs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('task_id', sa.Uuid(), nullable=False, comment='关联 scheduled_tasks.id'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False, comment='开始执行时间'),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True, comment='完成时间'),
        sa.Column('status', sa.String(20), nullable=False, server_default='running', comment='执行状态'),
        sa.Column('data_snapshot', sa.JSON(), nullable=True, comment='聚合数据快照'),
        sa.Column('card_content', sa.Text(), nullable=True, comment='发送的卡片 JSON'),
        sa.Column('feishu_msg_id', sa.String(100), nullable=True, comment='飞书消息 ID'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='错误信息'),
        sa.Column('duration_ms', sa.Integer(), nullable=True, comment='执行耗时（毫秒）'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.PrimaryKeyConstraint('id'),
        schema='safety',
    )
    op.create_index('ix_scheduled_task_logs_task_started', 'scheduled_task_logs', ['task_id', 'started_at'], schema='safety')


def downgrade() -> None:
    op.drop_index('ix_scheduled_task_logs_task_started', table_name='scheduled_task_logs', schema='safety')
    op.drop_table('scheduled_task_logs', schema='safety')
    op.drop_index('ix_scheduled_tasks_enabled_next', table_name='scheduled_tasks', schema='safety')
    op.drop_table('scheduled_tasks', schema='safety')
