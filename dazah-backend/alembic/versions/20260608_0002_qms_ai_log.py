"""AI 交互日志表迁移

Revision ID: qms_ai_log_001
Revises: dev_001
Create Date: 2026-06-08

创建 qms_ai_log 表用于记录 AI 交互日志。
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'qms_ai_log_001'
down_revision = 'dev_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建 qms schema 和 qms_ai_log 表"""
    # 创建 qms schema（如果不存在）
    op.execute('CREATE SCHEMA IF NOT EXISTS qms')

    # 创建 AI 交互日志表
    op.create_table(
        'qms_ai_log',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('bill_no', sa.String(length=100), nullable=True, comment='关联单据编号'),
        sa.Column('operate_type', sa.String(length=50), nullable=False, comment='操作类型'),
        sa.Column('operator', sa.String(length=100), nullable=False, comment='操作人账号'),
        sa.Column('system_prompt', sa.Text(), nullable=False, comment='系统提示词'),
        sa.Column('user_input', sa.Text(), nullable=False, comment='用户输入内容'),
        sa.Column('ai_response', sa.Text(), nullable=True, comment='AI 返回内容'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='错误信息'),
        sa.Column('tokens_used', sa.Integer(), nullable=True, comment='使用的 token 数量'),
        sa.Column('latency_ms', sa.Integer(), nullable=True, comment='响应耗时（毫秒）'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()'), comment='创建时间'),
        schema='qms'
    )

    # 创建索引
    op.create_index('idx_ai_log_bill_no', 'qms_ai_log', ['bill_no'], schema='qms')
    op.create_index('idx_ai_log_operate_type', 'qms_ai_log', ['operate_type'], schema='qms')
    op.create_index('idx_ai_log_operator', 'qms_ai_log', ['operator'], schema='qms')
    op.create_index('idx_ai_log_created_at', 'qms_ai_log', ['created_at'], schema='qms')


def downgrade() -> None:
    """删除 qms_ai_log 表和 qms schema"""
    op.drop_index('idx_ai_log_created_at', table_name='qms_ai_log', schema='qms')
    op.drop_index('idx_ai_log_operator', table_name='qms_ai_log', schema='qms')
    op.drop_index('idx_ai_log_operate_type', table_name='qms_ai_log', schema='qms')
    op.drop_index('idx_ai_log_bill_no', table_name='qms_ai_log', schema='qms')
    op.drop_table('qms_ai_log', schema='qms')
    # 注意：不删除 schema，保留其他可能的 qms 表