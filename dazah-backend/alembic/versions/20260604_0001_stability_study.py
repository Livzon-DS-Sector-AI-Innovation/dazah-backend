"""Stability Study (稳定性试验) migration

Revision ID: 20260604_0001
Revises: 20260603_0003
Create Date: 2026-06-04 09:00:00.000000

"""

from typing import Sequence
from uuid import uuid4

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = '20260604_0001'
down_revision: str = '20260603_0003'
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    # ========== 稳定性试验方案主表 ==========
    op.create_table(
        'stability_studies',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid4),
        # 方案编号
        sa.Column('study_no', sa.String(64), nullable=False, unique=True, comment='试验方案编号'),
        # 产品信息
        sa.Column('product_code', sa.String(64), nullable=False, comment='产品编码'),
        sa.Column('product_name', sa.String(255), nullable=True, comment='产品名称'),
        sa.Column('product_category', sa.String(32), nullable=True, comment='产品类别：api/intermediate/excipient'),
        # 批次信息
        sa.Column('batch_no', sa.String(64), nullable=False, comment='批号'),
        sa.Column('batch_quantity', sa.Numeric(18, 6), nullable=True, comment='批量'),
        sa.Column('packaging_spec', sa.String(255), nullable=True, comment='包装规格'),
        # 试验条件
        sa.Column('study_type', sa.String(32), nullable=False, comment='试验类型：long_term/accelerated/intermediate'),
        sa.Column('temperature', sa.String(32), nullable=True, comment='温度条件'),
        sa.Column('humidity', sa.String(32), nullable=True, comment='湿度条件'),
        # 试验周期
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=True, comment='试验开始日期'),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True, comment='试验结束日期'),
        sa.Column('expiry_date', sa.DateTime(timezone=True), nullable=True, comment='有效期'),
        # 取样周期
        sa.Column('sample_intervals', sa.String(255), nullable=True, comment='取样周期节点，逗号分隔：0,3,6,9,12,18,24'),
        # 质量标准
        sa.Column('standard_id', UUID(as_uuid=True), nullable=True, comment='关联质量标准ID'),
        sa.Column('standard_name', sa.String(255), nullable=True, comment='质量标准名称'),
        sa.Column('standard_version', sa.String(64), nullable=True, comment='标准版本'),
        # 方案负责人
        sa.Column('developer_id', UUID(as_uuid=True), nullable=True, comment='研发人员ID'),
        sa.Column('developer_name', sa.String(100), nullable=True, comment='研发人员'),
        # 状态
        sa.Column('status', sa.String(32), server_default='draft', nullable=False, comment='状态：draft/submitted/developer_approved/qc_supervisor_approved/qa_approved/final_approved/active/completed/closed'),
        # 方案状态
        sa.Column('study_conclusion', sa.String(32), nullable=True, comment='试验结论：qualified/conditional/unqualified'),
        sa.Column('conclusion_reason', sa.Text, nullable=True, comment='结论说明'),
        sa.Column('remark', sa.Text, nullable=True, comment='备注'),
        # 附件
        sa.Column('attachments', sa.Text, nullable=True, comment='附件JSON'),
        # 审计字段
        sa.Column('created_at', sa.DateTime(timezone=True), server_default='now()', nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default='now()', nullable=False),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean, server_default='false', nullable=False),
        schema='quality'
    )
    op.create_index('idx_stability_study_no', 'stability_studies', ['study_no'], unique=True, schema='quality')
    op.create_index('idx_stability_product_code', 'stability_studies', ['product_code'], schema='quality')
    op.create_index('idx_stability_batch_no', 'stability_studies', ['batch_no'], schema='quality')
    op.create_index('idx_stability_status', 'stability_studies', ['status'], schema='quality')
    op.create_index('idx_stability_study_type', 'stability_studies', ['study_type'], schema='quality')

    # ========== 稳定性取样节点表 ==========
    op.create_table(
        'stability_sample_nodes',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column('stability_study_id', UUID(as_uuid=True), nullable=False, comment='稳定性试验ID'),
        sa.Column('node_no', sa.Integer, nullable=False, comment='节点序号'),
        sa.Column('node_month', sa.Integer, nullable=False, comment='节点月数'),
        sa.Column('node_name', sa.String(64), nullable=True, comment='节点名称：0月/3月/6月...'),
        # 计划日期
        sa.Column('planned_date', sa.DateTime(timezone=True), nullable=True, comment='计划取样日期'),
        # 实际日期
        sa.Column('actual_date', sa.DateTime(timezone=True), nullable=True, comment='实际取样日期'),
        # 状态
        sa.Column('status', sa.String(32), server_default='pending', nullable=False, comment='状态：pending/sampling_done/inspection_done/overdue'),
        # 预警状态
        sa.Column('reminder_sent', sa.Boolean, server_default='false', nullable=False, comment='是否已发送预警'),
        sa.Column('reminder_date', sa.DateTime(timezone=True), nullable=True, comment='预警发送时间'),
        # 检验记录
        sa.Column('inspection_id', UUID(as_uuid=True), nullable=True, comment='关联检验记录ID'),
        sa.Column('inspection_no', sa.String(64), nullable=True, comment='检验记录编号'),
        sa.Column('inspection_status', sa.String(32), nullable=True, comment='检验状态'),
        sa.Column('inspection_conclusion', sa.String(32), nullable=True, comment='检验结论'),
        # 备注
        sa.Column('remark', sa.Text, nullable=True, comment='备注'),
        # 审计字段
        sa.Column('created_at', sa.DateTime(timezone=True), server_default='now()', nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default='now()', nullable=False),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean, server_default='false', nullable=False),
        sa.ForeignKeyConstraint(['stability_study_id'], ['quality.stability_studies.id'], ),
        schema='quality'
    )
    op.create_index('idx_sample_node_study_id', 'stability_sample_nodes', ['stability_study_id'], schema='quality')
    op.create_index('idx_sample_node_planned_date', 'stability_sample_nodes', ['planned_date'], schema='quality')
    op.create_index('idx_sample_node_status', 'stability_sample_nodes', ['status'], schema='quality')

    # ========== 稳定性检验记录表 ==========
    op.create_table(
        'stability_inspections',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid4),
        # 关联信息
        sa.Column('study_id', UUID(as_uuid=True), nullable=False, comment='稳定性试验ID'),
        sa.Column('study_no', sa.String(64), nullable=False, comment='试验方案编号'),
        sa.Column('sample_node_id', UUID(as_uuid=True), nullable=False, comment='取样节点ID'),
        sa.Column('node_month', sa.Integer, nullable=False, comment='节点月数'),
        # 检验单号
        sa.Column('inspection_no', sa.String(64), nullable=False, comment='检验单号'),
        # 产品信息
        sa.Column('product_code', sa.String(64), nullable=False, comment='产品编码'),
        sa.Column('product_name', sa.String(255), nullable=True, comment='产品名称'),
        sa.Column('batch_no', sa.String(64), nullable=False, comment='批号'),
        sa.Column('specification', sa.String(255), nullable=True, comment='规格/包装'),
        # 检验信息
        sa.Column('inspection_date', sa.DateTime(timezone=True), nullable=True, comment='检验日期'),
        sa.Column('inspector_id', UUID(as_uuid=True), nullable=True, comment='检验员ID'),
        sa.Column('inspector_name', sa.String(100), nullable=True, comment='检验员'),
        # 取样信息
        sa.Column('sample_quantity', sa.Numeric(18, 6), nullable=True, comment='取样数量'),
        sa.Column('sample_no', sa.String(64), nullable=True, comment='样品编号'),
        sa.Column('sample_condition', sa.String(128), nullable=True, comment='样品状态'),
        # 质量标准
        sa.Column('standard_id', UUID(as_uuid=True), nullable=True, comment='检验标准ID'),
        sa.Column('standard_name', sa.String(255), nullable=True, comment='质量标准名称'),
        # 检验结论
        sa.Column('status', sa.String(32), server_default='draft', nullable=False, comment='状态'),
        sa.Column('inspection_conclusion', sa.String(32), nullable=True, comment='检验结论'),
        sa.Column('conclusion_reason', sa.Text, nullable=True, comment='结论说明'),
        sa.Column('remark', sa.Text, nullable=True, comment='备注'),
        # OOS
        sa.Column('oos_report_no', sa.String(64), nullable=True, comment='OOS报告编号'),
        sa.Column('is_oos', sa.Boolean, server_default='false', nullable=False, comment='是否OOS'),
        # 附件
        sa.Column('attachments', sa.Text, nullable=True, comment='附件JSON'),
        # 审计字段
        sa.Column('created_at', sa.DateTime(timezone=True), server_default='now()', nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default='now()', nullable=False),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean, server_default='false', nullable=False),
        sa.ForeignKeyConstraint(['study_id'], ['quality.stability_studies.id'], ),
        sa.ForeignKeyConstraint(['sample_node_id'], ['quality.stability_sample_nodes.id'], ),
        schema='quality'
    )
    op.create_index('idx_stability_inspection_no', 'stability_inspections', ['inspection_no'], unique=True, schema='quality')
    op.create_index('idx_stability_inspection_study_id', 'stability_inspections', ['study_id'], schema='quality')
    op.create_index('idx_stability_inspection_node_id', 'stability_inspections', ['sample_node_id'], schema='quality')
    op.create_index('idx_stability_inspection_status', 'stability_inspections', ['status'], schema='quality')

    # ========== 稳定性检验明细表 ==========
    op.create_table(
        'stability_inspection_items',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column('stability_inspection_id', UUID(as_uuid=True), nullable=False, comment='稳定性检验ID'),
        sa.Column('item_no', sa.Integer, nullable=False, comment='项次'),
        sa.Column('inspection_item', sa.String(128), nullable=False, comment='检验项目名称'),
        sa.Column('inspection_method', sa.String(255), nullable=True, comment='检验方法'),
        sa.Column('standard_value', sa.String(255), nullable=True, comment='标准值/限度'),
        sa.Column('unit', sa.String(32), nullable=True, comment='单位'),
        sa.Column('measured_value', sa.String(255), nullable=True, comment='实测值'),
        sa.Column('result', sa.String(32), nullable=True, comment='单项判定：pass/fail/na'),
        sa.Column('is_oos', sa.Boolean, server_default='false', nullable=False, comment='是否超标'),
        sa.Column('oos_description', sa.Text, nullable=True, comment='超标描述'),
        # 趋势分析相关
        sa.Column('data_point', sa.String(64), nullable=True, comment='数据点：用于趋势分析'),
        # 图谱附件
        sa.Column('chromatogram_urls', sa.Text, nullable=True, comment='图谱附件JSON'),
        sa.Column('remark', sa.Text, nullable=True, comment='备注'),
        # 审计字段
        sa.Column('created_at', sa.DateTime(timezone=True), server_default='now()', nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default='now()', nullable=False),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean, server_default='false', nullable=False),
        sa.ForeignKeyConstraint(['stability_inspection_id'], ['quality.stability_inspections.id'], ),
        schema='quality'
    )
    op.create_index('idx_stability_items_inspection_id', 'stability_inspection_items', ['stability_inspection_id'], schema='quality')

    # ========== 稳定性审批记录表 ==========
    op.create_table(
        'stability_approval_records',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column('study_id', UUID(as_uuid=True), nullable=True, comment='稳定性试验ID'),
        sa.Column('inspection_id', UUID(as_uuid=True), nullable=True, comment='检验记录ID'),
        sa.Column('approval_type', sa.String(32), nullable=False, comment='审批类型：study/inspection'),
        sa.Column('approval_level', sa.Integer, nullable=False, comment='审批级别'),
        sa.Column('approval_status', sa.String(32), nullable=False, comment='审批状态：pending/approved/rejected'),
        sa.Column('approver_role', sa.String(64), nullable=True, comment='审批角色'),
        sa.Column('approver_id', UUID(as_uuid=True), nullable=True),
        sa.Column('approver_name', sa.String(100), nullable=True, comment='审批人姓名'),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True, comment='审批时间'),
        sa.Column('comments', sa.Text, nullable=True, comment='审批意见'),
        # 审计字段
        sa.Column('created_at', sa.DateTime(timezone=True), server_default='now()', nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default='now()', nullable=False),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean, server_default='false', nullable=False),
        sa.ForeignKeyConstraint(['study_id'], ['quality.stability_studies.id'], ),
        sa.ForeignKeyConstraint(['inspection_id'], ['quality.stability_inspections.id'], ),
        schema='quality'
    )
    op.create_index('idx_stability_approval_study_id', 'stability_approval_records', ['study_id'], schema='quality')
    op.create_index('idx_stability_approval_inspection_id', 'stability_approval_records', ['inspection_id'], schema='quality')


def downgrade() -> None:
    # 删除表（外键约束会随表一起删除）
    op.drop_table('stability_approval_records', schema='quality')
    op.drop_table('stability_inspection_items', schema='quality')
    op.drop_table('stability_inspections', schema='quality')
    op.drop_table('stability_sample_nodes', schema='quality')
    op.drop_table('stability_studies', schema='quality')
