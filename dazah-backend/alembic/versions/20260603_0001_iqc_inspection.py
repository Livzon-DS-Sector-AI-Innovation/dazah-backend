"""IQC inspection management tables

Revision ID: 20260603_0001
Revises: 20260602_0011
Create Date: 2026-06-03

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = '20260603_0001'
down_revision: Union[str, None] = '20260602_0011'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ========== IQC Inspections (IQC检验主表) ==========
    op.create_table(
        'iqc_inspections',
        sa.Column('inspection_no', sa.String(length=64), nullable=False, comment='检验单号'),
        sa.Column('sampling_order_id', sa.Uuid(), nullable=True, comment='关联取样单ID'),
        sa.Column('sampling_order_no', sa.String(length=64), nullable=True, comment='关联取样单号'),
        sa.Column('source_type', sa.String(length=32), nullable=False, comment='来源类型'),
        sa.Column('source_no', sa.String(length=64), nullable=True, comment='来源单号'),
        sa.Column('material_code', sa.String(length=64), nullable=False, comment='物料编码'),
        sa.Column('material_name', sa.String(length=255), nullable=True, comment='物料名称'),
        sa.Column('material_category', sa.String(length=32), nullable=True, comment='物料类别'),
        sa.Column('specification', sa.String(length=128), nullable=True, comment='规格'),
        sa.Column('batch_no', sa.String(length=64), nullable=True, comment='批次号'),
        sa.Column('supplier_code', sa.String(length=64), nullable=True, comment='供应商编码'),
        sa.Column('supplier_name', sa.String(length=255), nullable=True, comment='供应商名称'),
        sa.Column('manufacturing_date', sa.DateTime(timezone=True), nullable=True, comment='生产日期'),
        sa.Column('expiry_date', sa.DateTime(timezone=True), nullable=True, comment='有效期'),
        sa.Column('quantity_received', sa.Numeric(precision=18, scale=6), nullable=True, comment='到货数量'),
        sa.Column('unit', sa.String(length=32), nullable=True, comment='单位'),
        sa.Column('inspection_date', sa.DateTime(timezone=True), nullable=True, comment='检验日期'),
        sa.Column('inspector_id', sa.Uuid(), nullable=True, comment='检验员ID'),
        sa.Column('inspector_name', sa.String(length=100), nullable=True, comment='检验员姓名'),
        sa.Column('standard_id', sa.Uuid(), nullable=True, comment='检验标准ID'),
        sa.Column('standard_name', sa.String(length=255), nullable=True, comment='检验标准名称'),
        sa.Column('standard_version', sa.String(length=64), nullable=True, comment='标准版本'),
        sa.Column('status', sa.String(length=32), server_default=sa.text("'draft'"), nullable=False, comment='状态'),
        sa.Column('inspection_conclusion', sa.String(length=32), nullable=True, comment='检验结论'),
        sa.Column('remark', sa.Text(), nullable=True, comment='备注'),
        sa.Column('deviation_id', sa.Uuid(), nullable=True, comment='关联偏差ID'),
        sa.Column('id', sa.Uuid(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.ForeignKeyConstraint(['sampling_order_id'], ['quality.sampling_orders.id']),
        sa.ForeignKeyConstraint(['standard_id'], ['quality.inspection_standards.id']),
        sa.ForeignKeyConstraint(['created_by'], ['identity.users.id']),
        sa.ForeignKeyConstraint(['updated_by'], ['identity.users.id']),
        sa.PrimaryKeyConstraint('id'),
        schema='quality',
    )
    op.create_index('idx_iqc_inspection_no', 'iqc_inspections', ['inspection_no'], unique=True, schema='quality')
    op.create_index('idx_iqc_sampling_order_id', 'iqc_inspections', ['sampling_order_id'], schema='quality')
    op.create_index('idx_iqc_source_no', 'iqc_inspections', ['source_no'], schema='quality')
    op.create_index('idx_iqc_material_code', 'iqc_inspections', ['material_code'], schema='quality')
    op.create_index('idx_iqc_supplier_code', 'iqc_inspections', ['supplier_code'], schema='quality')
    op.create_index('idx_iqc_status', 'iqc_inspections', ['status'], schema='quality')
    op.create_index('idx_iqc_inspection_date', 'iqc_inspections', ['inspection_date'], schema='quality')

    # ========== IQC Inspection Items (IQC检验结果明细表) ==========
    op.create_table(
        'iqc_inspection_items',
        sa.Column('iqc_inspection_id', sa.Uuid(), nullable=False, comment='检验单ID'),
        sa.Column('item_no', sa.Integer(), nullable=False, comment='项次'),
        sa.Column('inspection_item', sa.String(length=128), nullable=False, comment='检验项目名称'),
        sa.Column('inspection_method', sa.String(length=255), nullable=True, comment='检验方法'),
        sa.Column('standard_value', sa.String(length=255), nullable=True, comment='标准值'),
        sa.Column('unit', sa.String(length=32), nullable=True, comment='单位'),
        sa.Column('measured_value', sa.String(length=255), nullable=True, comment='实测值'),
        sa.Column('result', sa.String(length=32), nullable=True, comment='单项判定'),
        sa.Column('is_repeat_test', sa.Boolean(), server_default=sa.text("false"), nullable=False, comment='是否复测'),
        sa.Column('raw_data', sa.Text(), nullable=True, comment='原始数据记录'),
        sa.Column('remark', sa.Text(), nullable=True, comment='备注'),
        sa.Column('id', sa.Uuid(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.ForeignKeyConstraint(['iqc_inspection_id'], ['quality.iqc_inspections.id']),
        sa.ForeignKeyConstraint(['created_by'], ['identity.users.id']),
        sa.ForeignKeyConstraint(['updated_by'], ['identity.users.id']),
        sa.PrimaryKeyConstraint('id'),
        schema='quality',
    )
    op.create_index('idx_iqc_items_inspection_id', 'iqc_inspection_items', ['iqc_inspection_id'], schema='quality')
    op.create_index('idx_iqc_items_item_no', 'iqc_inspection_items', ['item_no'], schema='quality')

    # ========== IQC Approval Records (IQC审批记录表) ==========
    op.create_table(
        'iqc_approval_records',
        sa.Column('iqc_inspection_id', sa.Uuid(), nullable=False, comment='检验单ID'),
        sa.Column('approval_level', sa.Integer(), nullable=False, comment='审批级别'),
        sa.Column('approval_status', sa.String(length=32), nullable=False, comment='审批状态'),
        sa.Column('approver_role', sa.String(length=64), nullable=True, comment='审批角色'),
        sa.Column('approver_id', sa.Uuid(), nullable=True, comment='审批人ID'),
        sa.Column('approver_name', sa.String(length=100), nullable=True, comment='审批人姓名'),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('id', sa.Uuid(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.ForeignKeyConstraint(['iqc_inspection_id'], ['quality.iqc_inspections.id']),
        sa.ForeignKeyConstraint(['approver_id'], ['identity.users.id']),
        sa.ForeignKeyConstraint(['created_by'], ['identity.users.id']),
        sa.ForeignKeyConstraint(['updated_by'], ['identity.users.id']),
        sa.PrimaryKeyConstraint('id'),
        schema='quality',
    )
    op.create_index('idx_iqc_approval_inspection_id', 'iqc_approval_records', ['iqc_inspection_id'], schema='quality')


def downgrade() -> None:
    op.drop_index('idx_iqc_approval_inspection_id', table_name='iqc_approval_records', schema='quality')
    op.drop_table('iqc_approval_records', schema='quality')
    op.drop_index('idx_iqc_items_item_no', table_name='iqc_inspection_items', schema='quality')
    op.drop_index('idx_iqc_items_inspection_id', table_name='iqc_inspection_items', schema='quality')
    op.drop_table('iqc_inspection_items', schema='quality')
    op.drop_index('idx_iqc_inspection_date', table_name='iqc_inspections', schema='quality')
    op.drop_index('idx_iqc_status', table_name='iqc_inspections', schema='quality')
    op.drop_index('idx_iqc_supplier_code', table_name='iqc_inspections', schema='quality')
    op.drop_index('idx_iqc_material_code', table_name='iqc_inspections', schema='quality')
    op.drop_index('idx_iqc_source_no', table_name='iqc_inspections', schema='quality')
    op.drop_index('idx_iqc_sampling_order_id', table_name='iqc_inspections', schema='quality')
    op.drop_index('idx_iqc_inspection_no', table_name='iqc_inspections', schema='quality')
    op.drop_table('iqc_inspections', schema='quality')