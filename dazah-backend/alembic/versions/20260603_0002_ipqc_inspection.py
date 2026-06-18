"""IPQC (In-Process Quality Control) inspection migration

Revision ID: 20260603_0002
Revises: 20260603_0001
Create Date: 2026-06-03 10:00:00.000000

"""
from typing import Sequence
from uuid import uuid4

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = '20260603_0002'
down_revision: str = '20260603_0001'
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    # ========== IPQC主表 ==========
    op.create_table(
        'ipqc_inspections',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column('inspection_no', sa.String(64), nullable=False, comment='检验单号'),
        sa.Column('batch_record_id', UUID(as_uuid=True), nullable=True, comment='关联批次生产记录ID'),
        sa.Column('batch_record_no', sa.String(64), nullable=True, comment='批次生产记录单号'),
        sa.Column('batch_no', sa.String(64), nullable=True, comment='批次号'),
        sa.Column('product_code', sa.String(64), nullable=False, comment='产品编码'),
        sa.Column('product_name', sa.String(255), nullable=True, comment='产品名称'),
        sa.Column('product_specification', sa.String(128), nullable=True, comment='产品规格'),
        sa.Column('process_stage', sa.String(64), nullable=True, comment='工序/工段'),
        sa.Column('sampling_point', sa.String(128), nullable=True, comment='取样点'),
        sa.Column('sampling_no', sa.String(64), nullable=True, comment='取样单号'),
        sa.Column('sampling_time', sa.DateTime(timezone=True), nullable=True, comment='取样时间'),
        sa.Column('sampling_quantity', sa.Numeric(18, 6), nullable=True, comment='取样数量'),
        sa.Column('sampling_unit', sa.String(32), nullable=True, comment='取样单位'),
        sa.Column('sampling_location', sa.String(255), nullable=True, comment='取样位置'),
        sa.Column('production_date', sa.DateTime(timezone=True), nullable=True, comment='生产日期'),
        # 检验信息
        sa.Column('inspection_date', sa.DateTime(timezone=True), nullable=True, comment='检验日期'),
        sa.Column('inspector_id', UUID(as_uuid=True), nullable=True, comment='检验员ID'),
        sa.Column('inspector_name', sa.String(100), nullable=True, comment='检验员姓名'),
        # 质量标准
        sa.Column('standard_id', UUID(as_uuid=True), nullable=True, comment='检验标准ID'),
        sa.Column('standard_name', sa.String(255), nullable=True, comment='检验标准名称'),
        sa.Column('standard_version', sa.String(64), nullable=True, comment='标准版本'),
        # 检验结论
        sa.Column('status', sa.String(32), server_default='draft', nullable=False, comment='状态：draft/submitted/workshop_approved/qc_supervisor_approved/qa_final_approved/rejected'),
        sa.Column('inspection_conclusion', sa.String(32), nullable=True, comment='检验结论：qualified/unqualified/conditional'),
        sa.Column('conclusion_reason', sa.Text, nullable=True, comment='结论说明'),
        sa.Column('remark', sa.Text, nullable=True, comment='备注'),
        sa.Column('deviation_id', UUID(as_uuid=True), nullable=True, comment='关联偏差ID'),
        sa.Column('oos_report_no', sa.String(64), nullable=True, comment='OOS报告编号'),
        # 批次状态
        sa.Column('batch_locked', sa.Boolean, server_default='false', nullable=False, comment='批次是否锁定'),
        sa.Column('batch_lock_reason', sa.Text, nullable=True, comment='批次锁定原因'),
        # 审计字段
        sa.Column('created_at', sa.DateTime(timezone=True), server_default='now()', nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default='now()', nullable=False),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean, server_default='false', nullable=False),
        schema='quality'
    )
    op.create_index('idx_ipqc_inspection_no', 'ipqc_inspections', ['inspection_no'], unique=True, schema='quality')
    op.create_index('idx_ipqc_batch_record_id', 'ipqc_inspections', ['batch_record_id'], schema='quality')
    op.create_index('idx_ipqc_batch_no', 'ipqc_inspections', ['batch_no'], schema='quality')
    op.create_index('idx_ipqc_product_code', 'ipqc_inspections', ['product_code'], schema='quality')
    op.create_index('idx_ipqc_status', 'ipqc_inspections', ['status'], schema='quality')
    op.create_index('idx_ipqc_inspection_date', 'ipqc_inspections', ['inspection_date'], schema='quality')
    op.create_index('idx_ipqc_sampling_time', 'ipqc_inspections', ['sampling_time'], schema='quality')

    # ========== IPQC检验项目明细表 ==========
    op.create_table(
        'ipqc_inspection_items',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column('ipqc_inspection_id', UUID(as_uuid=True), nullable=False, comment='IPQC检验单ID'),
        sa.Column('item_no', sa.Integer, nullable=False, comment='项次'),
        sa.Column('inspection_item', sa.String(128), nullable=False, comment='检验项目名称'),
        sa.Column('inspection_method', sa.String(255), nullable=True, comment='检验方法'),
        sa.Column('standard_value', sa.String(255), nullable=True, comment='标准值'),
        sa.Column('upper_limit', sa.String(64), nullable=True, comment='上限'),
        sa.Column('lower_limit', sa.String(64), nullable=True, comment='下限'),
        sa.Column('unit', sa.String(32), nullable=True, comment='单位'),
        sa.Column('measured_value', sa.String(255), nullable=True, comment='实测值'),
        sa.Column('result', sa.String(32), nullable=True, comment='单项判定：pass/fail/na'),
        sa.Column('is_repeat_test', sa.Boolean, server_default='false', nullable=False, comment='是否复测'),
        sa.Column('repeat_times', sa.Integer, server_default='0', nullable=False, comment='复测次数'),
        sa.Column('raw_data', sa.Text, nullable=True, comment='原始数据记录'),
        sa.Column('remark', sa.Text, nullable=True, comment='备注'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default='now()', nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default='now()', nullable=False),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean, server_default='false', nullable=False),
        sa.ForeignKeyConstraint(['ipqc_inspection_id'], ['quality.ipqc_inspections.id'], ),
        schema='quality'
    )
    op.create_index('idx_ipqc_items_inspection_id', 'ipqc_inspection_items', ['ipqc_inspection_id'], schema='quality')
    op.create_index('idx_ipqc_items_item_no', 'ipqc_inspection_items', ['item_no'], schema='quality')

    # ========== IPQC审批记录表 ==========
    op.create_table(
        'ipqc_approval_records',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column('ipqc_inspection_id', UUID(as_uuid=True), nullable=False, comment='IPQC检验单ID'),
        sa.Column('approval_level', sa.Integer, nullable=False, comment='审批级别：1-车间工艺负责人，2-QC主管复核，3-QA终审'),
        sa.Column('approval_status', sa.String(32), nullable=False, comment='审批状态：pending/approved/rejected'),
        sa.Column('approver_role', sa.String(64), nullable=True, comment='审批角色'),
        sa.Column('approver_id', UUID(as_uuid=True), nullable=True),
        sa.Column('approver_name', sa.String(100), nullable=True, comment='审批人姓名'),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True, comment='审批时间'),
        sa.Column('comments', sa.Text, nullable=True, comment='审批意见'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default='now()', nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default='now()', nullable=False),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean, server_default='false', nullable=False),
        sa.ForeignKeyConstraint(['ipqc_inspection_id'], ['quality.ipqc_inspections.id'], ),
        schema='quality'
    )
    op.create_index('idx_ipqc_approval_inspection_id', 'ipqc_approval_records', ['ipqc_inspection_id'], schema='quality')


def downgrade() -> None:
    # 删除表（外键约束会随表一起删除）
    op.drop_table('ipqc_approval_records', schema='quality')
    op.drop_table('ipqc_inspection_items', schema='quality')
    op.drop_table('ipqc_inspections', schema='quality')
