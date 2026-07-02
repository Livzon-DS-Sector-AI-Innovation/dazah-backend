"""backfill equipment orphan tables into alembic chain

Revision ID: ec9a6009d008
Revises: f8a7b2c3d4e5
Create Date: 2026-07-02 09:43:32.403385

补链：11 张由 create_all 建的孤儿表，用 inspector 检查幂等。
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = 'ec9a6009d008'
down_revision: Union[str, None] = 'f8a7b2c3d4e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# ─── BaseModel 共用列 ────────────────────────────────────────────
BM_COLS = [
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True),
              server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True),
              server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.Uuid(), nullable=True),
    sa.Column('updated_by', sa.Uuid(), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
]

BM_FK_PK = [
    sa.ForeignKeyConstraint(['created_by'], ['identity.users.id']),
    sa.ForeignKeyConstraint(['updated_by'], ['identity.users.id']),
    sa.PrimaryKeyConstraint('id'),
]


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)

    # ─── Level 1: 独立表 ──────────────────────────────────────────

    # 1. equipment_role
    if not inspector.has_table('equipment_role', schema='equipment'):
        op.create_table('equipment_role',
            sa.Column('name', sa.String(length=100), nullable=False,
                      comment='角色名称'),
            sa.Column('code', sa.String(length=50), nullable=False,
                      comment='角色编码'),
            sa.Column('description', sa.String(length=200), nullable=True,
                      comment='角色描述'),
            sa.Column('scope', sa.String(length=50),
                      server_default="'global'", comment='作用域'),
            sa.Column('is_active', sa.Boolean(), server_default='true',
                      comment='是否启用'),
            *BM_COLS,
            *BM_FK_PK,
            sa.UniqueConstraint('code', name='uq_equipment_role_code'),
            schema='equipment'
        )
        op.create_index('ix_equipment_role_scope_deleted',
                        'equipment_role', ['scope', 'is_deleted'],
                        schema='equipment')
    else:
        existing = inspector.get_indexes('equipment_role', schema='equipment')
        if not any(ix['name'] == 'ix_equipment_role_scope_deleted'
                   for ix in existing):
            op.create_index('ix_equipment_role_scope_deleted',
                            'equipment_role', ['scope', 'is_deleted'],
                            schema='equipment')

    # 2. equipment_personnel
    if not inspector.has_table('equipment_personnel', schema='equipment'):
        op.create_table('equipment_personnel',
            sa.Column('user_id', sa.Uuid(), nullable=True,
                      comment='逻辑引用 identity.users.id'),
            sa.Column('name', sa.String(length=100), nullable=False,
                      comment='冗余，人员姓名'),
            sa.Column('employee_no', sa.String(length=64), nullable=True,
                      comment='冗余，工号'),
            sa.Column('department', sa.String(length=200), nullable=True,
                      comment='冗余，部门'),
            sa.Column('feishu_user_id', sa.String(length=128), nullable=True,
                      comment='飞书 user_id（发消息通知用）'),
            sa.Column('feishu_open_id', sa.String(length=128), nullable=True,
                      comment='飞书 open_id'),
            sa.Column('mobile', sa.String(length=32), nullable=True,
                      comment='冗余，手机号'),
            sa.Column('extended_attrs', JSONB(), nullable=True,
                      comment='扩展属性槽'),
            sa.Column('is_active', sa.Boolean(), server_default='true',
                      comment='是否在岗'),
            *BM_COLS,
            *BM_FK_PK,
            schema='equipment'
        )
        op.create_index('ix_equipment_personnel_user_id',
                        'equipment_personnel', ['user_id'],
                        schema='equipment')
        op.create_index('ix_equipment_personnel_feishu_user_id',
                        'equipment_personnel', ['feishu_user_id'],
                        schema='equipment')
        op.create_index('ix_equipment_personnel_name',
                        'equipment_personnel', ['name'],
                        schema='equipment')
    else:
        existing = inspector.get_indexes('equipment_personnel',
                                         schema='equipment')
        for idx_name, idx_cols in [
            ('ix_equipment_personnel_user_id', ['user_id']),
            ('ix_equipment_personnel_feishu_user_id', ['feishu_user_id']),
            ('ix_equipment_personnel_name', ['name']),
        ]:
            if not any(ix['name'] == idx_name for ix in existing):
                op.create_index(idx_name, 'equipment_personnel',
                                idx_cols, schema='equipment')

    # 3. maintenance_config (updated_at 覆盖带 comment)
    if not inspector.has_table('maintenance_config', schema='equipment'):
        op.create_table('maintenance_config',
            sa.Column('config_key', sa.String(length=100), nullable=False,
                      comment='配置键'),
            sa.Column('config_value', sa.String(length=500), nullable=False,
                      comment='配置值'),
            # BaseModel 列 — updated_at 覆盖加 comment
            sa.Column('id', sa.Uuid(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True),
                      server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True),
                      server_default=sa.text('now()'), nullable=False,
                      comment='更新时间'),
            sa.Column('created_by', sa.Uuid(), nullable=True),
            sa.Column('updated_by', sa.Uuid(), nullable=True),
            sa.Column('is_deleted', sa.Boolean(), server_default='false',
                      nullable=False),
            sa.ForeignKeyConstraint(['created_by'], ['identity.users.id']),
            sa.ForeignKeyConstraint(['updated_by'], ['identity.users.id']),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('config_key',
                                name='uq_maintenance_config_config_key'),
            schema='equipment'
        )

    # 4. spare_parts
    if not inspector.has_table('spare_parts', schema='equipment'):
        op.create_table('spare_parts',
            sa.Column('code', sa.String(length=50), nullable=False,
                      comment='备件编码'),
            sa.Column('name', sa.String(length=200), nullable=False,
                      comment='备件名称'),
            sa.Column('specification', sa.String(length=200), nullable=True,
                      comment='规格型号'),
            sa.Column('unit', sa.String(length=20), nullable=False,
                      comment='计量单位'),
            sa.Column('category', sa.String(length=50), nullable=True,
                      comment='备件分类'),
            sa.Column('default_supplier', sa.String(length=200), nullable=True,
                      comment='默认供应商'),
            sa.Column('unit_price', sa.Numeric(precision=12, scale=2),
                      nullable=True, comment='参考单价'),
            sa.Column('is_active', sa.Boolean(), server_default='true',
                      comment='是否启用'),
            *BM_COLS,
            *BM_FK_PK,
            schema='equipment'
        )
        # partial unique index
        op.create_index(
            'uq_spare_parts_code', 'spare_parts', ['code'],
            unique=True, schema='equipment',
            postgresql_where=sa.text('is_deleted = false'),
        )
    else:
        existing = inspector.get_indexes('spare_parts', schema='equipment')
        if not any(ix['name'] == 'uq_spare_parts_code' for ix in existing):
            op.create_index(
                'uq_spare_parts_code', 'spare_parts', ['code'],
                unique=True, schema='equipment',
                postgresql_where=sa.text('is_deleted = false'),
            )

    # ─── Level 2: 只依赖 Level 1 或已在迁移链中的表 ───────────────

    # 5. equipment_personnel_role (逻辑引用，无强制 FK)
    if not inspector.has_table('equipment_personnel_role', schema='equipment'):
        op.create_table('equipment_personnel_role',
            sa.Column('personnel_id', sa.Uuid(), nullable=False,
                      comment='逻辑引用 equipment_personnel.id'),
            sa.Column('role_id', sa.Uuid(), nullable=False,
                      comment='逻辑引用 equipment_role.id'),
            *BM_COLS,
            *BM_FK_PK,
            sa.UniqueConstraint('personnel_id', 'role_id',
                                name='uq_equipment_personnel_role'),
            schema='equipment'
        )

    # 6. equipment_personnel_category (逻辑引用，无强制 FK)
    if not inspector.has_table('equipment_personnel_category',
                               schema='equipment'):
        op.create_table('equipment_personnel_category',
            sa.Column('personnel_id', sa.Uuid(), nullable=False,
                      comment='逻辑引用 equipment_personnel.id'),
            sa.Column('role_id', sa.Uuid(), nullable=False,
                      comment='逻辑引用 equipment_role.id'),
            sa.Column('category_id', sa.Uuid(), nullable=False,
                      comment='逻辑引用 equipment_categories.id'),
            *BM_COLS,
            *BM_FK_PK,
            sa.UniqueConstraint('personnel_id', 'role_id', 'category_id',
                                name='uq_equipment_personnel_category'),
            schema='equipment'
        )

    # 7. work_order_images (FK → work_orders，已在链中)
    if not inspector.has_table('work_order_images', schema='equipment'):
        op.create_table('work_order_images',
            sa.Column('work_order_id', sa.Uuid(), nullable=False,
                      comment='工单ID'),
            sa.Column('file_name', sa.String(length=255), nullable=False,
                      comment='原始文件名'),
            sa.Column('file_path', sa.String(length=500), nullable=False,
                      comment='服务器文件路径'),
            sa.Column('file_size', sa.Integer(), nullable=True,
                      comment='文件大小（字节）'),
            sa.Column('uploaded_at', sa.DateTime(timezone=True),
                      server_default=sa.text('now()'), nullable=False,
                      comment='上传时间'),
            *BM_COLS,
            *BM_FK_PK,
            sa.ForeignKeyConstraint(['work_order_id'],
                                    ['equipment.work_orders.id']),
            schema='equipment'
        )

    # 8. spare_part_stocks (FK → spare_parts)
    if not inspector.has_table('spare_part_stocks', schema='equipment'):
        op.create_table('spare_part_stocks',
            sa.Column('spare_part_id', sa.Uuid(), nullable=False,
                      comment='备件ID'),
            sa.Column('warehouse_location', sa.String(length=100),
                      nullable=True, comment='库位'),
            sa.Column('current_qty', sa.Integer(), server_default='0',
                      comment='当前库存'),
            sa.Column('safety_qty', sa.Integer(), server_default='0',
                      comment='安全库存'),
            sa.Column('min_order_qty', sa.Integer(), server_default='1',
                      comment='最小采购批量'),
            *BM_COLS,
            *BM_FK_PK,
            sa.ForeignKeyConstraint(['spare_part_id'],
                                    ['equipment.spare_parts.id']),
            sa.UniqueConstraint('spare_part_id',
                                name='uq_spare_part_stocks_spare_part_id'),
            schema='equipment'
        )

    # 9. equipment_spare_parts (FK → equipments + spare_parts)
    if not inspector.has_table('equipment_spare_parts', schema='equipment'):
        op.create_table('equipment_spare_parts',
            sa.Column('equipment_id', sa.Uuid(), nullable=False,
                      comment='设备ID'),
            sa.Column('spare_part_id', sa.Uuid(), nullable=False,
                      comment='备件ID'),
            sa.Column('quantity', sa.Integer(), nullable=False,
                      comment='该设备需要的数量'),
            *BM_COLS,
            *BM_FK_PK,
            sa.ForeignKeyConstraint(['equipment_id'],
                                    ['equipment.equipments.id']),
            sa.ForeignKeyConstraint(['spare_part_id'],
                                    ['equipment.spare_parts.id']),
            schema='equipment'
        )
        # partial unique index
        op.create_index(
            'uq_equipment_spare_parts_eq_sp', 'equipment_spare_parts',
            ['equipment_id', 'spare_part_id'],
            unique=True, schema='equipment',
            postgresql_where=sa.text('is_deleted = false'),
        )
    else:
        existing = inspector.get_indexes('equipment_spare_parts',
                                         schema='equipment')
        if not any(ix['name'] == 'uq_equipment_spare_parts_eq_sp'
                   for ix in existing):
            op.create_index(
                'uq_equipment_spare_parts_eq_sp', 'equipment_spare_parts',
                ['equipment_id', 'spare_part_id'],
                unique=True, schema='equipment',
                postgresql_where=sa.text('is_deleted = false'),
            )

    # ─── Level 3 ──────────────────────────────────────────────────

    # 10. maintenance_plans (FK → equipments + identity.users)
    if not inspector.has_table('maintenance_plans', schema='equipment'):
        op.create_table('maintenance_plans',
            sa.Column('equipment_id', sa.Uuid(), nullable=False,
                      comment='设备ID'),
            sa.Column('plan_name', sa.String(length=200), nullable=False,
                      comment='计划名称'),
            sa.Column('plan_type', sa.String(length=20), nullable=False,
                      comment='计划类型：预防性维护/预测性维护'),
            sa.Column('frequency', sa.Integer(), nullable=False,
                      comment='维护频率数值'),
            sa.Column('frequency_unit', sa.String(length=10), nullable=False,
                      comment='频率单位：天/周/月/年'),
            sa.Column('last_maintenance_date', sa.Date(), nullable=True,
                      comment='上次维护日期'),
            sa.Column('next_maintenance_date', sa.Date(), nullable=True,
                      comment='下次维护日期'),
            sa.Column('responsible_person_id', sa.Uuid(), nullable=True,
                      comment='负责人ID'),
            sa.Column('maintenance_content', sa.Text(), nullable=True,
                      comment='维护内容说明'),
            sa.Column('status', sa.String(length=10),
                      server_default='启用', comment='状态：启用/停用/已完成'),
            sa.Column('remark', sa.Text(), nullable=True, comment='备注'),
            sa.Column('last_generated_date', sa.Date(), nullable=True,
                      comment='最后生成工单的周期日期，用于防重'),
            *BM_COLS,
            sa.CheckConstraint(
                "plan_type IN ('预防性维护', '预测性维护')",
                name='ck_maintenance_plans_plan_type'),
            sa.CheckConstraint(
                "frequency_unit IN ('天', '周', '月', '年')",
                name='ck_maintenance_plans_frequency_unit'),
            sa.CheckConstraint(
                "status IN ('启用', '停用', '已完成')",
                name='ck_maintenance_plans_status'),
            *BM_FK_PK,
            sa.ForeignKeyConstraint(['equipment_id'],
                                    ['equipment.equipments.id']),
            sa.ForeignKeyConstraint(['responsible_person_id'],
                                    ['identity.users.id']),
            schema='equipment'
        )

    # 11. spare_part_transactions (FK → spare_parts + work_orders)
    if not inspector.has_table('spare_part_transactions',
                               schema='equipment'):
        op.create_table('spare_part_transactions',
            sa.Column('spare_part_id', sa.Uuid(), nullable=False,
                      comment='备件ID'),
            sa.Column('work_order_id', sa.Uuid(), nullable=True,
                      comment='关联工单ID'),
            sa.Column('transaction_type', sa.String(length=20),
                      nullable=False, comment='类型：入库/出库/盘点调整'),
            sa.Column('quantity', sa.Integer(), nullable=False,
                      comment='数量（正=入库，负=出库）'),
            sa.Column('remark', sa.Text(), nullable=True, comment='备注'),
            *BM_COLS,
            sa.CheckConstraint(
                "transaction_type IN ('入库', '出库', '盘点调整')",
                name='ck_spare_part_transactions_type'),
            *BM_FK_PK,
            sa.ForeignKeyConstraint(['spare_part_id'],
                                    ['equipment.spare_parts.id']),
            sa.ForeignKeyConstraint(['work_order_id'],
                                    ['equipment.work_orders.id']),
            schema='equipment'
        )


def downgrade() -> None:
    # Drop in reverse dependency order: Level 3 → Level 2 → Level 1
    # Indexes must drop before their tables

    # Level 3
    op.drop_table('spare_part_transactions', schema='equipment')
    op.drop_table('maintenance_plans', schema='equipment')

    # Level 2
    op.drop_index('uq_equipment_spare_parts_eq_sp',
                  table_name='equipment_spare_parts', schema='equipment',
                  postgresql_where=sa.text('is_deleted = false'))
    op.drop_table('equipment_spare_parts', schema='equipment')
    op.drop_table('spare_part_stocks', schema='equipment')
    op.drop_table('work_order_images', schema='equipment')
    op.drop_table('equipment_personnel_category', schema='equipment')
    op.drop_table('equipment_personnel_role', schema='equipment')

    # Level 1
    op.drop_index('uq_spare_parts_code', table_name='spare_parts',
                  schema='equipment',
                  postgresql_where=sa.text('is_deleted = false'))
    op.drop_table('spare_parts', schema='equipment')
    op.drop_table('maintenance_config', schema='equipment')
    op.drop_index('ix_equipment_personnel_name',
                  table_name='equipment_personnel', schema='equipment')
    op.drop_index('ix_equipment_personnel_feishu_user_id',
                  table_name='equipment_personnel', schema='equipment')
    op.drop_index('ix_equipment_personnel_user_id',
                  table_name='equipment_personnel', schema='equipment')
    op.drop_table('equipment_personnel', schema='equipment')
    op.drop_index('ix_equipment_role_scope_deleted',
                  table_name='equipment_role', schema='equipment')
    op.drop_table('equipment_role', schema='equipment')
