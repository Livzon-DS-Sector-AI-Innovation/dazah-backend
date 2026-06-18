"""FQC (Finished Product Quality Control) inspection migration

Revision ID: 20260603_0003
Revises: 20260603_0002
Create Date: 2026-06-03 12:00:00.000000

"""
from typing import Sequence
from uuid import uuid4

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = '20260603_0003'
down_revision: str = '20260603_0002'
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    # ========== FQC主表 ==========
    op.create_table(
        'fqc_inspections',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column('inspection_no', sa.String(64), nullable=False, comment='检验单号'),
        # 单据关联
        sa.Column('batch_record_id', UUID(as_uuid=True), nullable=True, comment='关联批生产记录ID'),
        sa.Column('batch_record_no', sa.String(64), nullable=True, comment='批生产记录编号'),
        sa.Column('batch_no', sa.String(64), nullable=True, comment='成品生产批号'),
        sa.Column('product_code', sa.String(64), nullable=False, comment='成品物料编码'),
        sa.Column('product_name', sa.String(255), nullable=True, comment='产品名称'),
        sa.Column('sampling_order_id', UUID(as_uuid=True), nullable=True, comment='入库取样单ID'),
        sa.Column('sampling_order_no', sa.String(64), nullable=True, comment='入库取样单号'),
        sa.Column('batch_quantity', sa.Numeric(18, 6), nullable=True, comment='批量'),
        sa.Column('production_workshop', sa.String(128), nullable=True, comment='生产车间'),
        # 基础信息
        sa.Column('cas_no', sa.String(64), nullable=True, comment='CAS号'),
        sa.Column('manufacturing_date', sa.DateTime(timezone=True), nullable=True, comment='生产日期'),
        sa.Column('expiry_date', sa.DateTime(timezone=True), nullable=True, comment='有效期至'),
        sa.Column('manufacturer', sa.String(255), nullable=True, comment='生产厂家'),
        sa.Column('specification', sa.String(128), nullable=True, comment='产品规格/包装'),
        # 检验信息
        sa.Column('inspection_date', sa.DateTime(timezone=True), nullable=True, comment='检验日期'),
        sa.Column('inspector_id', UUID(as_uuid=True), nullable=True, comment='检验员ID'),
        sa.Column('inspector_name', sa.String(100), nullable=True, comment='检验员'),
        # 质量标准
        sa.Column('standard_id', UUID(as_uuid=True), nullable=True, comment='检验标准ID'),
        sa.Column('standard_name', sa.String(255), nullable=True, comment='质量标准名称'),
        sa.Column('standard_version', sa.String(64), nullable=True, comment='标准版本'),
        # 检验结论
        sa.Column('status', sa.String(32), server_default='draft', nullable=False, comment='状态：draft/submitted/qc_supervisor_approved/qa_approved/final_approved/released/locked/closed'),
        sa.Column('inspection_conclusion', sa.String(32), nullable=True, comment='检验结论：qualified/unqualified'),
        sa.Column('conclusion_reason', sa.Text, nullable=True, comment='结论说明'),
        sa.Column('remark', sa.Text, nullable=True, comment='备注'),
        # OOS与偏差
        sa.Column('oos_report_no', sa.String(64), nullable=True, comment='OOS报告编号'),
        sa.Column('deviation_id', UUID(as_uuid=True), nullable=True, comment='关联偏差ID'),
        # 批次状态
        sa.Column('batch_locked', sa.Boolean, server_default='false', nullable=False, comment='批次是否锁定'),
        sa.Column('batch_lock_reason', sa.Text, nullable=True, comment='批次锁定原因'),
        sa.Column('warehouse_isolation', sa.Boolean, server_default='false', nullable=False, comment='是否入库隔离'),
        # 放行状态
        sa.Column('release_status', sa.String(32), nullable=True, comment='放行状态：pending_release/released/not_released'),
        sa.Column('release_reason', sa.Text, nullable=True, comment='放行说明'),
        # 复检
        sa.Column('reinspection_applied', sa.Boolean, server_default='false', nullable=False, comment='是否申请复检'),
        sa.Column('reinspection_reason', sa.Text, nullable=True, comment='复检原因'),
        # 附件
        sa.Column('attachments', sa.Text, nullable=True, comment='附件JSON，存储文件信息'),
        # 检验报告
        sa.Column('report_no', sa.String(64), nullable=True, comment='检验报告书编号'),
        sa.Column('report_url', sa.String(512), nullable=True, comment='检验报告书URL'),
        # 审计字段
        sa.Column('created_at', sa.DateTime(timezone=True), server_default='now()', nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default='now()', nullable=False),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean, server_default='false', nullable=False),
        schema='quality'
    )
    op.create_index('idx_fqc_inspection_no', 'fqc_inspections', ['inspection_no'], unique=True, schema='quality')
    op.create_index('idx_fqc_batch_record_id', 'fqc_inspections', ['batch_record_id'], schema='quality')
    op.create_index('idx_fqc_batch_no', 'fqc_inspections', ['batch_no'], schema='quality')
    op.create_index('idx_fqc_product_code', 'fqc_inspections', ['product_code'], schema='quality')
    op.create_index('idx_fqc_status', 'fqc_inspections', ['status'], schema='quality')
    op.create_index('idx_fqc_inspection_date', 'fqc_inspections', ['inspection_date'], schema='quality')
    op.create_index('idx_fqc_release_status', 'fqc_inspections', ['release_status'], schema='quality')

    # ========== FQC检验结果明细表 ==========
    op.create_table(
        'fqc_inspection_items',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column('fqc_inspection_id', UUID(as_uuid=True), nullable=False, comment='FQC检验单ID'),
        sa.Column('item_no', sa.Integer, nullable=False, comment='项次'),
        sa.Column('inspection_category', sa.String(64), nullable=True, comment='检验类别：content/related_substances/residual_solvents/physical_chemical/microbiology'),
        sa.Column('inspection_item', sa.String(128), nullable=False, comment='检验项目名称'),
        sa.Column('inspection_method', sa.String(255), nullable=True, comment='检验方法'),
        sa.Column('standard_value', sa.String(255), nullable=True, comment='标准值/限度'),
        sa.Column('unit', sa.String(32), nullable=True, comment='单位'),
        sa.Column('measured_value', sa.String(255), nullable=True, comment='实测值'),
        sa.Column('result', sa.String(32), nullable=True, comment='单项判定：pass/fail/na'),
        sa.Column('is_oos', sa.Boolean, server_default='false', nullable=False, comment='是否超标'),
        sa.Column('oos_description', sa.Text, nullable=True, comment='超标描述'),
        sa.Column('is_repeat_test', sa.Boolean, server_default='false', nullable=False, comment='是否复测'),
        sa.Column('repeat_times', sa.Integer, server_default='0', nullable=False, comment='复测次数'),
        # 附件
        sa.Column('chromatogram_urls', sa.Text, nullable=True, comment='图谱附件JSON'),
        sa.Column('raw_record_url', sa.String(512), nullable=True, comment='原始记录PDF URL'),
        sa.Column('remark', sa.Text, nullable=True, comment='备注'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default='now()', nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default='now()', nullable=False),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean, server_default='false', nullable=False),
        sa.ForeignKeyConstraint(['fqc_inspection_id'], ['quality.fqc_inspections.id'], ),
        schema='quality'
    )
    op.create_index('idx_fqc_items_inspection_id', 'fqc_inspection_items', ['fqc_inspection_id'], schema='quality')
    op.create_index('idx_fqc_items_item_no', 'fqc_inspection_items', ['item_no'], schema='quality')

    # ========== FQC审批记录表 ==========
    op.create_table(
        'fqc_approval_records',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column('fqc_inspection_id', UUID(as_uuid=True), nullable=False, comment='FQC检验单ID'),
        sa.Column('approval_level', sa.Integer, nullable=False, comment='审批级别：1-QC主管，2-QA，3-质量负责人'),
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
        sa.ForeignKeyConstraint(['fqc_inspection_id'], ['quality.fqc_inspections.id'], ),
        schema='quality'
    )
    op.create_index('idx_fqc_approval_inspection_id', 'fqc_approval_records', ['fqc_inspection_id'], schema='quality')


def downgrade() -> None:
    # 删除表（外键约束会随表一起删除）
    op.drop_table('fqc_approval_records', schema='quality')
    op.drop_table('fqc_inspection_items', schema='quality')
    op.drop_table('fqc_inspections', schema='quality')
