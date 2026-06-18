"""Instrument Calibration (仪器校准管理) migration

Revision ID: 20260604_0002
Revises: 20260604_0001
Create Date: 2026-06-04 14:00:00.000000

"""

from typing import Sequence
from uuid import uuid4

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = '20260604_0002'
down_revision: str = '20260604_0001'
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    # ========== 仪器设备台账主表 ==========
    op.create_table(
        'instrument_calibrations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid4),
        # 仪器基本信息
        sa.Column('instrument_no', sa.String(64), nullable=False, unique=True, comment='仪器编号'),
        sa.Column('instrument_name', sa.String(255), nullable=False, comment='仪器名称'),
        sa.Column('model', sa.String(255), nullable=True, comment='型号'),
        sa.Column('serial_no', sa.String(128), nullable=True, comment='出厂编号'),
        sa.Column('manufacturer', sa.String(255), nullable=True, comment='制造商'),
        # 存放信息
        sa.Column('location', sa.String(255), nullable=True, comment='存放地点'),
        # 仪器分类
        sa.Column('category', sa.String(32), nullable=True, comment='仪器分类：physicochemical/chromatography/microbiology/balance/oven/other'),
        # 出厂信息
        sa.Column('manufacture_date', sa.DateTime(timezone=True), nullable=True, comment='出厂日期'),
        # IQ/OQ确认状态
        sa.Column('iq_status', sa.String(32), nullable=True, comment='IQ确认状态：pending/confirmed/not_required'),
        sa.Column('oq_status', sa.String(32), nullable=True, comment='OQ确认状态：pending/confirmed/not_required'),
        sa.Column('iq_confirm_date', sa.DateTime(timezone=True), nullable=True, comment='IQ确认日期'),
        sa.Column('oq_confirm_date', sa.DateTime(timezone=True), nullable=True, comment='OQ确认日期'),
        # 使用负责人
        sa.Column('responsible_id', UUID(as_uuid=True), nullable=True, comment='使用负责人ID'),
        sa.Column('responsible_name', sa.String(100), nullable=True, comment='使用负责人'),
        # 启用状态
        sa.Column('is_active', sa.Boolean, server_default='true', nullable=False, comment='是否启用'),
        sa.Column('deactivate_date', sa.DateTime(timezone=True), nullable=True, comment='停用日期'),
        sa.Column('deactivate_reason', sa.Text, nullable=True, comment='停用原因'),
        # 设备状态
        sa.Column('status', sa.String(32), server_default='draft', nullable=False, comment='状态：draft/submitted/admin_approved/qa_approved/active/inactive'),
        # 备注
        sa.Column('remark', sa.Text, nullable=True, comment='备注'),
        # 审计字段
        sa.Column('created_at', sa.DateTime(timezone=True), server_default='now()', nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default='now()', nullable=False),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean, server_default='false', nullable=False),
        schema='quality'
    )
    op.create_index('idx_instrument_no', 'instrument_calibrations', ['instrument_no'], unique=True, schema='quality')
    op.create_index('idx_instrument_name', 'instrument_calibrations', ['instrument_name'], schema='quality')
    op.create_index('idx_instrument_category', 'instrument_calibrations', ['category'], schema='quality')
    op.create_index('idx_instrument_status', 'instrument_calibrations', ['status'], schema='quality')
    op.create_index('idx_instrument_active', 'instrument_calibrations', ['is_active'], schema='quality')

    # ========== 仪器校准规则配置表 ==========
    op.create_table(
        'instrument_calibration_rules',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column('instrument_id', UUID(as_uuid=True), nullable=False, comment='关联仪器ID'),
        # 校准方式
        sa.Column('calibration_method', sa.String(32), nullable=False, comment='校准方式：external/internal'),
        # 校准周期
        sa.Column('calibration_cycle', sa.Integer, nullable=True, comment='校准周期（月）'),
        sa.Column('calibration_unit', sa.String(32), nullable=True, comment='周期单位：month/year'),
        # 最近校准信息
        sa.Column('last_calibration_date', sa.DateTime(timezone=True), nullable=True, comment='最近校准日期'),
        sa.Column('next_calibration_date', sa.DateTime(timezone=True), nullable=True, comment='下次校准日期'),
        # 校准机构（外校时）
        sa.Column('calibration_agency', sa.String(255), nullable=True, comment='校准机构名称'),
        sa.Column('agency_contact', sa.String(255), nullable=True, comment='机构联系方式'),
        # 内校人员
        sa.Column('internal_calibrator_id', UUID(as_uuid=True), nullable=True, comment='内校人员ID'),
        sa.Column('internal_calibrator_name', sa.String(100), nullable=True, comment='内校人员'),
        # 到期预警
        sa.Column('warning_days', sa.Integer, server_default='7', nullable=True, comment='提前预警天数'),
        # 是否启用
        sa.Column('is_active', sa.Boolean, server_default='true', nullable=False, comment='是否启用'),
        # 审计字段
        sa.Column('created_at', sa.DateTime(timezone=True), server_default='now()', nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default='now()', nullable=False),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True),
        schema='quality'
    )
    op.create_index('idx_rule_instrument', 'instrument_calibration_rules', ['instrument_id'], schema='quality')
    op.create_index('idx_rule_next_date', 'instrument_calibration_rules', ['next_calibration_date'], schema='quality')

    # ========== 仪器校准记录表 ==========
    op.create_table(
        'instrument_calibration_records',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column('instrument_id', UUID(as_uuid=True), nullable=False, comment='关联仪器ID'),
        sa.Column('rule_id', UUID(as_uuid=True), nullable=True, comment='关联校准规则ID'),
        # 校准单据信息
        sa.Column('calibration_no', sa.String(64), nullable=False, unique=True, comment='校准单据编号'),
        # 校准日期
        sa.Column('calibration_date', sa.DateTime(timezone=True), nullable=False, comment='校准日期'),
        sa.Column('calibration_end_date', sa.DateTime(timezone=True), nullable=True, comment='校准完成日期'),
        # 校准机构/人员
        sa.Column('calibration_method', sa.String(32), nullable=False, comment='校准方式：external/internal'),
        sa.Column('calibration_agency', sa.String(255), nullable=True, comment='校准机构'),
        sa.Column('calibrator_id', UUID(as_uuid=True), nullable=True, comment='校准人员ID'),
        sa.Column('calibrator_name', sa.String(100), nullable=True, comment='校准人员'),
        # 校准证书
        sa.Column('certificate_no', sa.String(128), nullable=True, comment='校准证书编号'),
        sa.Column('certificate_url', sa.String(512), nullable=True, comment='校准证书附件URL'),
        # 校准结论
        sa.Column('calibration_result', sa.String(32), nullable=False, comment='校准结论：qualified/unqualified/limited'),
        sa.Column('result_reason', sa.Text, nullable=True, comment='结论说明'),
        # 有效期
        sa.Column('valid_from', sa.DateTime(timezone=True), nullable=True, comment='有效期起'),
        sa.Column('valid_until', sa.DateTime(timezone=True), nullable=True, comment='有效期至'),
        # 计划信息
        sa.Column('is_scheduled', sa.Boolean, server_default='false', nullable=False, comment='是否计划校准'),
        sa.Column('scheduled_date', sa.DateTime(timezone=True), nullable=True, comment='计划校准日期'),
        # 审核状态
        sa.Column('status', sa.String(32), server_default='draft', nullable=False, comment='状态：draft/submitted/admin_approved/qa_approved/completed'),
        # 备注
        sa.Column('remark', sa.Text, nullable=True, comment='备注'),
        # 审计字段
        sa.Column('created_at', sa.DateTime(timezone=True), server_default='now()', nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default='now()', nullable=False),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean, server_default='false', nullable=False),
        schema='quality'
    )
    op.create_index('idx_calibration_no', 'instrument_calibration_records', ['calibration_no'], unique=True, schema='quality')
    op.create_index('idx_calibration_instrument', 'instrument_calibration_records', ['instrument_id'], schema='quality')
    op.create_index('idx_calibration_date', 'instrument_calibration_records', ['calibration_date'], schema='quality')
    op.create_index('idx_calibration_result', 'instrument_calibration_records', ['calibration_result'], schema='quality')
    op.create_index('idx_calibration_status', 'instrument_calibration_records', ['status'], schema='quality')

    # ========== 审批记录表 ==========
    op.create_table(
        'instrument_calibration_approvals',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid4),
        # 关联类型：instrument/record
        sa.Column('related_type', sa.String(32), nullable=False, comment='关联类型：instrument/record'),
        sa.Column('related_id', UUID(as_uuid=True), nullable=False, comment='关联ID'),
        # 审批流程
        sa.Column('approval_type', sa.String(32), nullable=False, comment='审批类型：admin_approval/qa_approval'),
        sa.Column('sequence', sa.Integer, server_default='1', nullable=False, comment='审批顺序'),
        # 审批状态
        sa.Column('status', sa.String(32), server_default='pending', nullable=False, comment='审批状态：pending/approved/rejected'),
        sa.Column('approval_date', sa.DateTime(timezone=True), nullable=True, comment='审批日期'),
        sa.Column('comments', sa.Text, nullable=True, comment='审批意见'),
        # 审批人
        sa.Column('approver_id', UUID(as_uuid=True), nullable=True, comment='审批人ID'),
        sa.Column('approver_name', sa.String(100), nullable=True, comment='审批人'),
        # 审计字段
        sa.Column('created_at', sa.DateTime(timezone=True), server_default='now()', nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default='now()', nullable=False),
        schema='quality'
    )
    op.create_index('idx_approval_related', 'instrument_calibration_approvals', ['related_type', 'related_id'], schema='quality')
    op.create_index('idx_approval_status', 'instrument_calibration_approvals', ['status'], schema='quality')


def downgrade() -> None:
    op.drop_table('instrument_calibration_approvals', schema='quality')
    op.drop_table('instrument_calibration_records', schema='quality')
    op.drop_table('instrument_calibration_rules', schema='quality')
    op.drop_table('instrument_calibrations', schema='quality')
