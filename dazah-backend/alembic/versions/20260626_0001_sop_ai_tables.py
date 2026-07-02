"""SOP AI 文件合规校验表迁移

Revision ID: sop_ai_001
Revises: 20260623_0001_add_calibration_reminder_config
Create Date: 2026-06-26

创建 SOP AI 模块的三张表：
- sop_ai_config: 配置表
- sop_ai_check_main: 校验主表
- sop_ai_check_problem: 问题明细表
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'sop_ai_001'
down_revision = '20260623_0001'
branch_labels = None
depends_on = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建 SOP AI 模块表"""

    # 创建 sop_ai_config 表
    op.create_table(
        'sop_ai_config',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('config_key', sa.String(length=100), nullable=False, unique=True, comment='配置键'),
        sa.Column('config_value', sa.Text(), nullable=False, comment='配置值'),
        sa.Column('description', sa.String(length=500), nullable=True, comment='配置描述'),
        sa.Column('operator', sa.String(length=100), nullable=True, comment='操作人'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.Column('created_by', sa.String(length=100), nullable=True, comment='创建人'),
        sa.Column('updated_by', sa.String(length=100), nullable=True, comment='更新人'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('FALSE'), comment='是否删除')
    )
    op.create_index('idx_sop_ai_config_key', 'sop_ai_config', ['config_key'])

    # 创建 sop_ai_check_main 表
    op.create_table(
        'sop_ai_check_main',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('file_code', sa.String(length=100), nullable=True, comment='文件编号'),
        sa.Column('file_name', sa.String(length=500), nullable=False, comment='文件名称'),
        sa.Column('file_path', sa.String(length=1000), nullable=True, comment='文件路径'),
        sa.Column('file_type', sa.String(length=20), nullable=True, comment='文件类型'),
        sa.Column('file_version', sa.String(length=50), nullable=True, comment='文件版本'),
        sa.Column('check_type', sa.String(length=20), nullable=False, comment='校验类型'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending', comment='状态'),
        sa.Column('operator', sa.String(length=100), nullable=True, comment='操作人'),
        sa.Column('total_problems', sa.Integer(), nullable=False, server_default='0', comment='问题总数'),
        sa.Column('high_risk_count', sa.Integer(), nullable=False, server_default='0', comment='高风险数'),
        sa.Column('medium_risk_count', sa.Integer(), nullable=False, server_default='0', comment='中风险数'),
        sa.Column('low_risk_count', sa.Integer(), nullable=False, server_default='0', comment='低风险数'),
        sa.Column('duration_ms', sa.Integer(), nullable=True, comment='耗时（毫秒）'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.Column('created_by', sa.String(length=100), nullable=True, comment='创建人'),
        sa.Column('updated_by', sa.String(length=100), nullable=True, comment='更新人'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('FALSE'), comment='是否删除')
    )
    op.create_index('idx_sop_ai_check_main_code', 'sop_ai_check_main', ['file_code'])
    op.create_index('idx_sop_ai_check_main_status', 'sop_ai_check_main', ['status'])
    op.create_index('idx_sop_ai_check_main_type', 'sop_ai_check_main', ['check_type'])
    op.create_index('idx_sop_ai_check_main_created', 'sop_ai_check_main', ['created_at'])

    # 创建 sop_ai_check_problem 表
    op.create_table(
        'sop_ai_check_problem',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('main_id', postgresql.UUID(as_uuid=True), nullable=False, comment='主任务ID'),
        sa.Column('problem_type', sa.String(length=50), nullable=False, comment='问题类型'),
        sa.Column('risk_level', sa.String(length=20), nullable=False, comment='风险等级'),
        sa.Column('title', sa.String(length=500), nullable=False, comment='问题标题'),
        sa.Column('description', sa.Text(), nullable=True, comment='问题描述'),
        sa.Column('location', sa.String(length=500), nullable=True, comment='位置'),
        sa.Column('source_file', sa.String(length=500), nullable=True, comment='来源文件'),
        sa.Column('suggestion', sa.Text(), nullable=True, comment='整改建议'),
        sa.Column('handle_status', sa.String(length=20), nullable=False, server_default='pending', comment='处理状态'),
        sa.Column('handle_note', sa.Text(), nullable=True, comment='处理备注'),
        sa.Column('handled_by', sa.String(length=100), nullable=True, comment='处理人'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('FALSE'), comment='是否删除')
    )
    op.create_index('idx_sop_ai_check_problem_main', 'sop_ai_check_problem', ['main_id'])
    op.create_index('idx_sop_ai_check_problem_type', 'sop_ai_check_problem', ['problem_type'])
    op.create_index('idx_sop_ai_check_problem_risk', 'sop_ai_check_problem', ['risk_level'])
    op.create_index('idx_sop_ai_check_problem_status', 'sop_ai_check_problem', ['handle_status'])


def downgrade() -> None:
    """删除 SOP AI 模块表"""
    op.drop_table('sop_ai_check_problem')
    op.drop_table('sop_ai_check_main')
    op.drop_table('sop_ai_config')