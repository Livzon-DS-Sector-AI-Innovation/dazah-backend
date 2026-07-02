"""add inspection tables

Revision ID: f8a7b2c3d4e5
Revises: c1f3a4b5d6e7
Create Date: 2026-07-01 10:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f8a7b2c3d4e5'
down_revision: Union[str, None] = 'c1f3a4b5d6e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. 基础表（无外键依赖或仅依赖已存在的表）
    op.create_table('inspection_templates',
    sa.Column('name', sa.String(length=200), nullable=False, comment='模板名称'),
    sa.Column('description', sa.Text(), nullable=True, comment='模板描述'),
    sa.Column('equipment_category_id', sa.Uuid(), nullable=True, comment='适用设备分类ID'),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False, comment='是否启用'),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.Uuid(), nullable=True),
    sa.Column('updated_by', sa.Uuid(), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['identity.users.id'], ),
    sa.ForeignKeyConstraint(['equipment_category_id'], ['equipment.equipment_categories.id'], ),
    sa.ForeignKeyConstraint(['updated_by'], ['identity.users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='equipment'
    )

    op.create_table('inspection_template_items',
    sa.Column('template_id', sa.Uuid(), nullable=False, comment='模板ID'),
    sa.Column('item_name', sa.String(length=200), nullable=False, comment='检查项名称'),
    sa.Column('item_description', sa.Text(), nullable=True, comment='检查项说明'),
    sa.Column('expected_result', sa.String(length=200), nullable=True, comment='预期结果/标准值'),
    sa.Column('check_method', sa.String(length=100), nullable=True, comment='检查方法'),
    sa.Column('sort_order', sa.Integer(), server_default='0', nullable=False, comment='排序序号'),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.Uuid(), nullable=True),
    sa.Column('updated_by', sa.Uuid(), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['identity.users.id'], ),
    sa.ForeignKeyConstraint(['template_id'], ['equipment.inspection_templates.id'], ),
    sa.ForeignKeyConstraint(['updated_by'], ['identity.users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='equipment'
    )

    op.create_table('inspection_routes',
    sa.Column('name', sa.String(length=200), nullable=False, comment='路线名称'),
    sa.Column('description', sa.Text(), nullable=True, comment='路线描述'),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False, comment='是否启用'),
    sa.Column('period_type', sa.String(length=20), nullable=False, comment='巡检周期类型'),
    sa.Column('period_value', sa.Integer(), nullable=True, comment='周期数值'),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.Uuid(), nullable=True),
    sa.Column('updated_by', sa.Uuid(), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
    sa.CheckConstraint("period_type IN ('每日', '每周', '每月', '专项')", name='ck_inspection_routes_period_type'),
    sa.ForeignKeyConstraint(['created_by'], ['identity.users.id'], ),
    sa.ForeignKeyConstraint(['updated_by'], ['identity.users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name', 'is_deleted', name='uq_inspection_routes_name'),
    schema='equipment'
    )

    # 2. route_locations (depends on inspection_routes + locations)
    op.create_table('route_locations',
    sa.Column('route_id', sa.Uuid(), nullable=False, comment='路线ID'),
    sa.Column('location_id', sa.Uuid(), nullable=False, comment='地点ID'),
    sa.Column('sort_order', sa.Integer(), server_default='0', nullable=False, comment='地点巡检顺序'),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.Uuid(), nullable=True),
    sa.Column('updated_by', sa.Uuid(), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['identity.users.id'], ),
    sa.ForeignKeyConstraint(['location_id'], ['equipment.locations.id'], ),
    sa.ForeignKeyConstraint(['route_id'], ['equipment.inspection_routes.id'], ),
    sa.ForeignKeyConstraint(['updated_by'], ['identity.users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='equipment'
    )
    op.create_index('uq_route_locations_active', 'route_locations', ['route_id', 'location_id'], unique=True, schema='equipment', postgresql_where=sa.text('is_deleted = false'))

    # 3. route_location_equipments (depends on route_locations + equipments)
    op.create_table('route_location_equipments',
    sa.Column('route_location_id', sa.Uuid(), nullable=False, comment='线路地点ID'),
    sa.Column('equipment_id', sa.Uuid(), nullable=False, comment='设备ID'),
    sa.Column('sort_order', sa.Integer(), server_default='0', nullable=False, comment='地点内设备顺序'),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.Uuid(), nullable=True),
    sa.Column('updated_by', sa.Uuid(), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['identity.users.id'], ),
    sa.ForeignKeyConstraint(['equipment_id'], ['equipment.equipments.id'], ),
    sa.ForeignKeyConstraint(['route_location_id'], ['equipment.route_locations.id'], ),
    sa.ForeignKeyConstraint(['updated_by'], ['identity.users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='equipment'
    )
    op.create_index('uq_route_location_equipments_active', 'route_location_equipments', ['route_location_id', 'equipment_id'], unique=True, schema='equipment', postgresql_where=sa.text('is_deleted = false'))

    # 4. route_equipment_templates (depends on route_location_equipments + inspection_templates)
    op.create_table('route_equipment_templates',
    sa.Column('route_equipment_id', sa.Uuid(), nullable=False, comment='线路地点设备ID'),
    sa.Column('template_id', sa.Uuid(), nullable=False, comment='巡检模板ID'),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.Uuid(), nullable=True),
    sa.Column('updated_by', sa.Uuid(), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['identity.users.id'], ),
    sa.ForeignKeyConstraint(['route_equipment_id'], ['equipment.route_location_equipments.id'], ),
    sa.ForeignKeyConstraint(['template_id'], ['equipment.inspection_templates.id'], ),
    sa.ForeignKeyConstraint(['updated_by'], ['identity.users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='equipment'
    )
    op.create_index('uq_route_equipment_templates_active', 'route_equipment_templates', ['route_equipment_id', 'template_id'], unique=True, schema='equipment', postgresql_where=sa.text('is_deleted = false'))

    # 5. inspection_tasks (depends on inspection_routes + equipments + users)
    op.create_table('inspection_tasks',
    sa.Column('task_no', sa.String(length=50), nullable=False, comment='任务编号 IT-yyyymmdd-xxxx'),
    sa.Column('route_id', sa.Uuid(), nullable=True, comment='关联路线ID（路线模式）'),
    sa.Column('equipment_id', sa.Uuid(), nullable=True, comment='单设备ID（单设备模式，兼容旧数据）'),
    sa.Column('equipment_ids', sa.JSON(), nullable=True, comment='设备ID列表（多设备模式）'),
    sa.Column('template_ids', sa.JSON(), nullable=True, comment='[DEPRECATED] 模板ID列表，推荐用 equipment_templates'),
    sa.Column('equipment_templates', sa.JSON(), nullable=True, comment='设备-模板绑定 {equipment_id: [template_id,...]}'),
    sa.Column('plan_type', sa.String(length=20), nullable=False, comment='巡检类型：线路巡检/设备巡检'),
    sa.Column('assigned_to', sa.Uuid(), nullable=True, comment='巡检人员ID'),
    sa.Column('planned_time', sa.DateTime(timezone=True), nullable=False, comment='计划巡检时间'),
    sa.Column('status', sa.String(length=20), nullable=False, comment='任务状态：待执行/执行中/已完成/已关闭'),
    sa.Column('overall_result', sa.String(length=10), nullable=True, comment='总体结果：正常/异常'),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=True, comment='开始时间'),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True, comment='完成时间'),
    sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True, comment='关闭时间'),
    sa.Column('closure_remark', sa.Text(), nullable=True, comment='关闭备注'),
    sa.Column('route_summary', sa.Text(), nullable=True, comment='线路巡检现场描述'),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.Uuid(), nullable=True),
    sa.Column('updated_by', sa.Uuid(), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
    sa.CheckConstraint("status IN ('待执行', '执行中', '已完成', '已关闭')", name='ck_inspection_tasks_status'),
    sa.CheckConstraint("plan_type IN ('线路巡检', '设备巡检')", name='ck_inspection_tasks_plan_type'),
    sa.CheckConstraint("overall_result IS NULL OR overall_result IN ('正常', '异常')", name='ck_inspection_tasks_overall_result'),
    sa.ForeignKeyConstraint(['assigned_to'], ['identity.users.id'], ),
    sa.ForeignKeyConstraint(['created_by'], ['identity.users.id'], ),
    sa.ForeignKeyConstraint(['equipment_id'], ['equipment.equipments.id'], ),
    sa.ForeignKeyConstraint(['route_id'], ['equipment.inspection_routes.id'], ),
    sa.ForeignKeyConstraint(['updated_by'], ['identity.users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('task_no', 'is_deleted', name='uq_inspection_tasks_task_no'),
    schema='equipment'
    )

    # 6. 依赖 inspection_tasks 的表
    op.create_table('inspection_records',
    sa.Column('task_id', sa.Uuid(), nullable=False, comment='关联巡检任务ID'),
    sa.Column('route_location_id', sa.Uuid(), nullable=True, comment='关联线路地点（线路巡检时标记）'),
    sa.Column('equipment_id', sa.Uuid(), nullable=True, comment='关联设备ID'),
    sa.Column('template_item_id', sa.Uuid(), nullable=False, comment='检查项ID'),
    sa.Column('result', sa.String(length=20), nullable=False, comment='结果：正常/异常/跳过'),
    sa.Column('actual_value', sa.String(length=200), nullable=True, comment='实际值'),
    sa.Column('remark', sa.Text(), nullable=True, comment='备注'),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.Uuid(), nullable=True),
    sa.Column('updated_by', sa.Uuid(), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['identity.users.id'], ),
    sa.ForeignKeyConstraint(['equipment_id'], ['equipment.equipments.id'], ),
    sa.ForeignKeyConstraint(['route_location_id'], ['equipment.route_locations.id'], ),
    sa.ForeignKeyConstraint(['task_id'], ['equipment.inspection_tasks.id'], ),
    sa.ForeignKeyConstraint(['template_item_id'], ['equipment.inspection_template_items.id'], ),
    sa.ForeignKeyConstraint(['updated_by'], ['identity.users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='equipment'
    )

    op.create_table('inspection_photos',
    sa.Column('task_id', sa.Uuid(), nullable=False, comment='巡检任务ID'),
    sa.Column('equipment_id', sa.Uuid(), nullable=True, comment='设备ID（线路巡检时可为空）'),
    sa.Column('file_name', sa.String(length=255), nullable=False, comment='原始文件名'),
    sa.Column('file_path', sa.String(length=500), nullable=False, comment='服务器文件路径'),
    sa.Column('file_size', sa.Integer(), nullable=True, comment='文件大小（字节）'),
    sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='上传时间'),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.Uuid(), nullable=True),
    sa.Column('updated_by', sa.Uuid(), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['identity.users.id'], ),
    sa.ForeignKeyConstraint(['equipment_id'], ['equipment.equipments.id'], ),
    sa.ForeignKeyConstraint(['task_id'], ['equipment.inspection_tasks.id'], ),
    sa.ForeignKeyConstraint(['updated_by'], ['identity.users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='equipment'
    )

    # 7. DEPRECATED: 旧路线-设备关联表，保留兼容
    op.create_table('inspection_route_equipments',
    sa.Column('route_id', sa.Uuid(), nullable=False, comment='路线ID'),
    sa.Column('equipment_id', sa.Uuid(), nullable=False, comment='设备ID'),
    sa.Column('sort_order', sa.Integer(), nullable=False, comment='巡检顺序'),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.Uuid(), nullable=True),
    sa.Column('updated_by', sa.Uuid(), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['identity.users.id'], ),
    sa.ForeignKeyConstraint(['equipment_id'], ['equipment.equipments.id'], ),
    sa.ForeignKeyConstraint(['route_id'], ['equipment.inspection_routes.id'], ),
    sa.ForeignKeyConstraint(['updated_by'], ['identity.users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('route_id', 'equipment_id', 'is_deleted', name='uq_route_equipments_route_equipment'),
    schema='equipment'
    )


def downgrade() -> None:
    op.drop_table('inspection_route_equipments', schema='equipment')
    op.drop_table('inspection_photos', schema='equipment')
    op.drop_table('inspection_records', schema='equipment')
    op.drop_table('inspection_tasks', schema='equipment')
    op.drop_index('uq_route_equipment_templates_active', table_name='route_equipment_templates', schema='equipment', postgresql_where=sa.text('is_deleted = false'))
    op.drop_table('route_equipment_templates', schema='equipment')
    op.drop_index('uq_route_location_equipments_active', table_name='route_location_equipments', schema='equipment', postgresql_where=sa.text('is_deleted = false'))
    op.drop_table('route_location_equipments', schema='equipment')
    op.drop_index('uq_route_locations_active', table_name='route_locations', schema='equipment', postgresql_where=sa.text('is_deleted = false'))
    op.drop_table('route_locations', schema='equipment')
    op.drop_table('inspection_routes', schema='equipment')
    op.drop_table('inspection_template_items', schema='equipment')
    op.drop_table('inspection_templates', schema='equipment')
