"""add_energy_workshop_and_monthly

Revision ID: add_energy_workshop
Revises: 21e7046001c0
Create Date: 2026-06-30

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_energy_workshop'
down_revision = '21e7046001c0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建 energy schema（如果不存在）
    op.execute("CREATE SCHEMA IF NOT EXISTS energy")
    
    # 创建车间表
    op.create_table(
        'energy_workshops',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('code', sa.String(50), nullable=False, comment='车间编码'),
        sa.Column('name', sa.String(100), nullable=False, comment='车间名称'),
        sa.Column('category', sa.String(20), nullable=False, comment='分类: workshop/position/support/utility'),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True, comment='父级车间ID'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0', comment='排序'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', comment='是否启用'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_by', sa.String(100), nullable=True),
        sa.Column('updated_by', sa.String(100), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        schema='energy',
    )
    
    # 创建唯一约束
    op.create_unique_constraint('uq_energy_workshop_code', 'energy_workshops', ['code'], schema='energy')
    
    # 创建月度记录表
    op.create_table(
        'energy_monthly_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('workshop_id', postgresql.UUID(as_uuid=True), nullable=False, comment='车间ID'),
        sa.Column('energy_type', sa.String(20), nullable=False, comment='能源类型'),
        sa.Column('record_date', sa.Date(), nullable=False, comment='记录日期'),
        sa.Column('date_range_end', sa.Date(), nullable=True, comment='日期范围结束'),
        sa.Column('value', sa.Numeric(18, 4), nullable=False, comment='能耗值'),
        sa.Column('unit', sa.String(20), nullable=False, comment='计量单位'),
        sa.Column('source', sa.String(50), nullable=False, server_default='feishu', comment='数据来源'),
        sa.Column('remark', sa.Text(), nullable=True, comment='备注'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_by', sa.String(100), nullable=True),
        sa.Column('updated_by', sa.String(100), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        schema='energy',
    )
    
    # 创建唯一约束
    op.create_unique_constraint(
        'uq_energy_monthly_record',
        'energy_monthly_records',
        ['workshop_id', 'energy_type', 'record_date'],
        schema='energy'
    )
    
    # 更新 energy_device_configs 表的 energy_type 约束
    op.drop_constraint('ck_energy_device_config_energy_type', 'energy_device_configs', schema='energy')
    op.create_check_constraint(
        'ck_energy_device_config_energy_type',
        'energy_device_configs',
        "energy_type IN ('electricity', 'water', 'gas', 'steam')",
        schema='energy'
    )
    
    # 更新 energy_alert_rules 表的 energy_type 约束
    op.drop_constraint('ck_energy_alert_rule_energy_type', 'energy_alert_rules', schema='energy')
    op.create_check_constraint(
        'ck_energy_alert_rule_energy_type',
        'energy_alert_rules',
        "energy_type IN ('electricity', 'water', 'gas', 'steam')",
        schema='energy'
    )


def downgrade() -> None:
    # 恢复约束
    op.drop_constraint('ck_energy_alert_rule_energy_type', 'energy_alert_rules', schema='energy')
    op.create_check_constraint(
        'ck_energy_alert_rule_energy_type',
        'energy_alert_rules',
        "energy_type IN ('electricity', 'water', 'gas')",
        schema='energy'
    )
    
    op.drop_constraint('ck_energy_device_config_energy_type', 'energy_device_configs', schema='energy')
    op.create_check_constraint(
        'ck_energy_device_config_energy_type',
        'energy_device_configs',
        "energy_type IN ('electricity', 'water', 'gas')",
        schema='energy'
    )
    
    # 删除表
    op.drop_table('energy_monthly_records', schema='energy')
    op.drop_table('energy_workshops', schema='energy')
