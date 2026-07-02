"""添加校准到期提醒配置表

Revision ID: 20260623_0001_add_calibration_reminder_config
Revises: 20260611_0001_material_report
Create Date: 2026-06-23 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '20260623_0001'
down_revision = 'material_report_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建校准到期提醒配置表
    op.create_table(
        'calibration_reminder_config',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(100), nullable=False, comment='配置名称'),
        sa.Column('feishu_app_id', sa.String(100), nullable=True, comment='飞书应用AppID'),
        sa.Column('feishu_app_secret', sa.String(255), nullable=True, comment='飞书应用AppSecret'),
        sa.Column('chat_id', sa.String(255), nullable=True, comment='飞书群ID或用户ID'),
        sa.Column('receive_id_type', sa.String(20), nullable=False, default='chat_id', server_default='chat_id', comment='接收类型: chat_id/user_id'),
        sa.Column('remind_30_days', sa.Boolean, nullable=False, default=True, server_default='true', comment='是否在30天前提醒'),
        sa.Column('remind_14_days', sa.Boolean, nullable=False, default=True, server_default='true', comment='是否在14天前提醒'),
        sa.Column('remind_7_days', sa.Boolean, nullable=False, default=True, server_default='true', comment='是否在7天前提醒'),
        sa.Column('remind_overdue', sa.Boolean, nullable=False, default=True, server_default='true', comment='是否在超期后提醒'),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True, server_default='true', comment='是否启用'),
        sa.Column('last_remind_30_days', sa.DateTime(timezone=True), nullable=True, comment='上次30天提醒时间'),
        sa.Column('last_remind_14_days', sa.DateTime(timezone=True), nullable=True, comment='上次14天提醒时间'),
        sa.Column('last_remind_7_days', sa.DateTime(timezone=True), nullable=True, comment='上次7天提醒时间'),
        sa.Column('last_remind_overdue', sa.DateTime(timezone=True), nullable=True, comment='上次超期提醒时间'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean, nullable=False, default=False, server_default='false', comment='是否删除'),
        comment='校准到期提醒配置表',
        schema='quality',
    )

    # 创建索引
    op.create_index('idx_reminder_config_is_active', 'calibration_reminder_config', ['is_active'], schema='quality')


def downgrade() -> None:
    op.drop_index('idx_reminder_config_is_active', 'calibration_reminder_config', schema='quality')
    op.drop_table('calibration_reminder_config', schema='quality')
