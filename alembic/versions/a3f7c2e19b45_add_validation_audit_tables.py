"""add validation audit tables

Revision ID: a3f7c2e19b45
Revises: 206c1eaf5c87
Create Date: 2026-06-18 16:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a3f7c2e19b45'
down_revision: Union[str, None] = '206c1eaf5c87'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # registration schema already exists (created by baseline)

    # ── validation_audit_tasks ──
    op.create_table(
        'validation_audit_tasks',
        sa.Column('task_name', sa.String(300), nullable=False, comment='任务名称'),
        sa.Column('product_name', sa.String(200), nullable=False, comment='品种名称'),
        sa.Column('method_name', sa.String(300), nullable=False, comment='方法名称'),
        sa.Column('source_company', sa.String(300), nullable=False, comment='来源公司'),
        sa.Column('audit_mode', sa.String(30), nullable=False, comment='审核模式: protocol/report/protocol_report'),
        sa.Column('status', sa.String(30), nullable=False, server_default='draft', comment='状态'),
        sa.Column('conclusion', sa.String(30), nullable=True, comment='审核结论'),
        sa.Column('risk_level', sa.String(30), nullable=True, comment='风险等级'),
        sa.Column('serious_count', sa.Integer(), nullable=False, server_default='0', comment='严重问题数'),
        sa.Column('general_count', sa.Integer(), nullable=False, server_default='0', comment='一般问题数'),
        sa.Column('suggestion_count', sa.Integer(), nullable=False, server_default='0', comment='建议优化数'),
        sa.Column('compliant_count', sa.Integer(), nullable=False, server_default='0', comment='合规项数'),
        sa.Column('non_compliant_count', sa.Integer(), nullable=False, server_default='0', comment='不合规项数'),
        sa.Column('report_path', sa.String(500), nullable=True, comment='审核报告文件路径'),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.PrimaryKeyConstraint('id'),
        schema='registration',
    )
    op.create_index('ix_validation_audit_tasks_status', 'validation_audit_tasks', ['status'], schema='registration')
    op.create_index('ix_validation_audit_tasks_source_company', 'validation_audit_tasks', ['source_company'], schema='registration')

    # ── validation_audit_files ──
    op.create_table(
        'validation_audit_files',
        sa.Column('task_id', sa.Uuid(), nullable=False, comment='任务ID'),
        sa.Column('file_type', sa.String(30), nullable=False, comment='文件类型'),
        sa.Column('original_filename', sa.String(500), nullable=False, comment='原始文件名'),
        sa.Column('file_path', sa.String(500), nullable=False, comment='文件存储路径'),
        sa.Column('file_size', sa.Integer(), nullable=False, server_default='0', comment='文件大小'),
        sa.Column('parse_status', sa.String(30), nullable=False, server_default='pending', comment='解析状态'),
        sa.Column('parsed_text', sa.Text(), nullable=True, comment='解析后文本'),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.PrimaryKeyConstraint('id'),
        schema='registration',
    )
    op.create_index('ix_validation_audit_files_task_id', 'validation_audit_files', ['task_id'], schema='registration')

    # ── validation_audit_issues ──
    op.create_table(
        'validation_audit_issues',
        sa.Column('task_id', sa.Uuid(), nullable=False, comment='任务ID'),
        sa.Column('file_id', sa.Uuid(), nullable=True, comment='文件ID'),
        sa.Column('issue_no', sa.String(20), nullable=False, comment='问题编号'),
        sa.Column('dimension', sa.String(100), nullable=False, comment='所属维度'),
        sa.Column('check_item', sa.String(200), nullable=False, comment='检查项'),
        sa.Column('description', sa.Text(), nullable=False, comment='问题描述'),
        sa.Column('suggestion', sa.Text(), nullable=True, comment='修改建议'),
        sa.Column('issue_type', sa.String(20), nullable=False, comment='问题类型'),
        sa.Column('page_no', sa.Integer(), nullable=True, comment='所在页码'),
        sa.Column('evidence_text', sa.Text(), nullable=True, comment='证据原文'),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.PrimaryKeyConstraint('id'),
        schema='registration',
    )
    op.create_index('ix_validation_audit_issues_task_id', 'validation_audit_issues', ['task_id'], schema='registration')
    op.create_index('ix_validation_audit_issues_file_id', 'validation_audit_issues', ['file_id'], schema='registration')

    # ── validation_audit_reports ──
    op.create_table(
        'validation_audit_reports',
        sa.Column('task_id', sa.Uuid(), nullable=False, comment='任务ID'),
        sa.Column('report_title', sa.String(500), nullable=False, comment='报告标题'),
        sa.Column('report_markdown', sa.Text(), nullable=True, comment='报告Markdown内容'),
        sa.Column('report_file_path', sa.String(500), nullable=True, comment='报告文件路径'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1', comment='报告版本'),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.PrimaryKeyConstraint('id'),
        schema='registration',
    )
    op.create_index('ix_validation_audit_reports_task_id', 'validation_audit_reports', ['task_id'], schema='registration')

    # ── validation_audit_knowledge_base ──
    op.create_table(
        'validation_audit_knowledge_base',
        sa.Column('dimension', sa.String(100), nullable=False, comment='所属维度'),
        sa.Column('check_item', sa.String(200), nullable=False, comment='检查项'),
        sa.Column('issue_type', sa.String(20), nullable=False, comment='问题类型'),
        sa.Column('description_template', sa.Text(), nullable=True, comment='问题描述模板'),
        sa.Column('suggestion_template', sa.Text(), nullable=True, comment='修改建议模板'),
        sa.Column('frequency', sa.Integer(), nullable=False, server_default='1', comment='出现频次'),
        sa.Column('related_product', sa.String(200), nullable=True, comment='涉及品种'),
        sa.Column('source_task_id', sa.Uuid(), nullable=True, comment='来源任务ID'),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.PrimaryKeyConstraint('id'),
        schema='registration',
    )
    op.create_index('ix_validation_audit_kb_source_task_id', 'validation_audit_knowledge_base', ['source_task_id'], schema='registration')


def downgrade() -> None:
    op.drop_index('ix_validation_audit_kb_source_task_id', table_name='validation_audit_knowledge_base', schema='registration')
    op.drop_table('validation_audit_knowledge_base', schema='registration')

    op.drop_index('ix_validation_audit_reports_task_id', table_name='validation_audit_reports', schema='registration')
    op.drop_table('validation_audit_reports', schema='registration')

    op.drop_index('ix_validation_audit_issues_file_id', table_name='validation_audit_issues', schema='registration')
    op.drop_index('ix_validation_audit_issues_task_id', table_name='validation_audit_issues', schema='registration')
    op.drop_table('validation_audit_issues', schema='registration')

    op.drop_index('ix_validation_audit_files_task_id', table_name='validation_audit_files', schema='registration')
    op.drop_table('validation_audit_files', schema='registration')

    op.drop_index('ix_validation_audit_tasks_source_company', table_name='validation_audit_tasks', schema='registration')
    op.drop_index('ix_validation_audit_tasks_status', table_name='validation_audit_tasks', schema='registration')
    op.drop_table('validation_audit_tasks', schema='registration')
