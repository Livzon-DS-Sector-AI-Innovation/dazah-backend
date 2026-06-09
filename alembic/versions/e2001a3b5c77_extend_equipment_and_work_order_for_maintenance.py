"""extend equipment and work_order for maintenance

Revision ID: e2001a3b5c77
Revises: 1e3a6f5002da
Create Date: 2026-06-04 10:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e2001a3b5c77'
down_revision: Union[str, None] = '1e3a6f5002da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Equipment new columns

    # Stub tables for FK references (full implementation in P3/P4)
    op.create_table(
        'maintenance_plans',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='equipment',
    )
    op.create_table(
        'inspection_templates',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='equipment',
    )

    # WorkOrder new columns

    # Add FK constraints for the new columns
    op.create_foreign_key(
        'fk_work_orders_maintenance_plan_id',
        'work_orders',
        'maintenance_plans',
        ['maintenance_plan_id'],
        ['id'],
        source_schema='equipment',
        referent_schema='equipment',
    )
    op.create_foreign_key(
        'fk_work_orders_checklist_template_id',
        'work_orders',
        'inspection_templates',
        ['checklist_template_id'],
        ['id'],
        source_schema='equipment',
        referent_schema='equipment',
    )

    # Update order_type check constraint to include 计划维护 and 巡检
    op.drop_constraint('ck_work_orders_order_type', 'work_orders', schema='equipment')
    op.create_check_constraint(
        'ck_work_orders_order_type',
        'work_orders',
        "order_type IN ('故障维修', '计划维护', '巡检', '校准')",
        schema='equipment',
    )

    # Update status check constraint to include 待执行 and 执行中
    op.drop_constraint('ck_work_orders_status', 'work_orders', schema='equipment')
    op.create_check_constraint(
        'ck_work_orders_status',
        'work_orders',
        "status IN ('待处理', '已指派', '维修中', '待验收', '已完成', '已关闭', '待执行', '执行中')",
        schema='equipment',
    )


def downgrade() -> None:
    # Revert status check constraint
    op.drop_constraint('ck_work_orders_status', 'work_orders', schema='equipment')
    op.create_check_constraint(
        'ck_work_orders_status',
        'work_orders',
        "status IN ('待处理', '已指派', '维修中', '待验收', '已完成', '已关闭')",
        schema='equipment',
    )

    # Revert order_type check constraint
    op.drop_constraint('ck_work_orders_order_type', 'work_orders', schema='equipment')
    op.create_check_constraint(
        'ck_work_orders_order_type',
        'work_orders',
        "order_type IN ('故障维修', '校准')",
        schema='equipment',
    )

    # Drop FK constraints
    op.drop_constraint('fk_work_orders_checklist_template_id', 'work_orders', schema='equipment')
    op.drop_constraint('fk_work_orders_maintenance_plan_id', 'work_orders', schema='equipment')

    # Remove WorkOrder columns
    op.drop_column('work_orders', 'spare_parts_cost', schema='equipment')
    op.drop_column('work_orders', 'check_result', schema='equipment')
    op.drop_column('work_orders', 'checklist_template_id', schema='equipment')
    op.drop_column('work_orders', 'planned_start_date', schema='equipment')
    op.drop_column('work_orders', 'maintenance_plan_id', schema='equipment')

    # Drop stub tables
    op.drop_table('inspection_templates', schema='equipment')
    op.drop_table('maintenance_plans', schema='equipment')

    # Remove Equipment columns
    op.drop_column('equipments', 'technical_params', schema='equipment')
    op.drop_column('equipments', 'depreciation_years', schema='equipment')
    op.drop_column('equipments', 'asset_value', schema='equipment')
    op.drop_column('equipments', 'warranty_expire_date', schema='equipment')
