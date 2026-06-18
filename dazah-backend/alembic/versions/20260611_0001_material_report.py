"""原料报告单模块数据库迁移

Revision ID: material_report_001
Revises: investigation_conclusion_001
Create Date: 2026-06-11

创建原料报告单模块相关表：
1. report_templates - 报告单模板管理表
2. material_reports - 报告单主表
3. material_report_items - 报告单明细表
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'material_report_001'
down_revision = '20260610_0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建原料报告单模块相关表"""

    # 1. 创建报告单模板管理表
    op.create_table(
        'report_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('template_name', sa.String(length=255), nullable=False, comment='模板名称'),
        sa.Column('template_file_url', sa.String(length=500), nullable=False, comment='模板文件存储路径'),
        sa.Column('template_description', sa.Text(), nullable=True, comment='模板描述说明'),
        sa.Column('field_mapping', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}', comment='静态字段映射配置'),
        sa.Column('table_fields', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}', comment='动态表格字段定义'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', comment='是否启用'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, onupdate=sa.text('NOW()'), comment='更新时间'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True, comment='创建人'),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True, comment='更新人'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false', comment='软删除标记'),
        schema='quality'
    )

    # 2. 创建报告单主表
    op.create_table(
        'material_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('report_no', sa.String(length=64), nullable=False, comment='报告单编号'),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=True, comment='关联模板ID'),
        sa.Column('report_title', sa.String(length=255), nullable=False, comment='报告单标题'),
        sa.Column('report_date', sa.Date(), nullable=False, comment='报告日期'),
        sa.Column('static_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='静态字段数据'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='draft', comment='状态'),
        sa.Column('generated_file_url', sa.String(length=500), nullable=True, comment='生成文件路径'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, onupdate=sa.text('NOW()'), comment='更新时间'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True, comment='创建人'),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True, comment='更新人'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false', comment='软删除标记'),
        schema='quality'
    )

    # 3. 创建报告单明细表
    op.create_table(
        'material_report_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('report_id', postgresql.UUID(as_uuid=True), nullable=False, comment='关联报告单ID'),
        sa.Column('row_index', sa.Integer(), nullable=False, comment='行序号'),
        sa.Column('field_key', sa.String(length=100), nullable=False, comment='字段标识'),
        sa.Column('field_value', sa.Text(), nullable=True, comment='字段值'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()'), comment='创建时间'),
        schema='quality'
    )

    # 创建唯一约束
    op.create_unique_constraint('uq_report_no', 'quality.material_reports', ['report_no'])
    op.create_unique_constraint('uq_item_composite', 'quality.material_report_items', ['report_id', 'row_index', 'field_key'])

    # 创建索引
    op.create_index('idx_template_name', 'quality.report_templates', ['template_name'], unique=True)
    op.create_index('idx_template_active', 'quality.report_templates', ['is_active'])
    op.create_index('idx_report_template', 'quality.material_reports', ['template_id'])
    op.create_index('idx_report_status', 'quality.material_reports', ['status'])
    op.create_index('idx_report_date', 'quality.material_reports', ['report_date'])
    op.create_index('idx_item_report', 'quality.material_report_items', ['report_id'])
    op.create_index('idx_item_row', 'quality.material_report_items', ['row_index'])


def downgrade() -> None:
    """删除原料报告单模块相关表"""
    # 删除索引
    op.drop_index('idx_item_row', table_name='material_report_items', schema='quality')
    op.drop_index('idx_item_report', table_name='material_report_items', schema='quality')
    op.drop_index('idx_report_date', table_name='material_reports', schema='quality')
    op.drop_index('idx_report_status', table_name='material_reports', schema='quality')
    op.drop_index('idx_report_template', table_name='material_reports', schema='quality')
    op.drop_index('idx_template_active', table_name='report_templates', schema='quality')
    op.drop_index('idx_template_name', table_name='report_templates', schema='quality')

    # 删除唯一约束
    op.drop_constraint('uq_item_composite', 'quality.material_report_items', schema='quality')
    op.drop_constraint('uq_report_no', 'quality.material_reports', schema='quality')

    # 删除表（注意顺序，先删明细表，再删主表，最后删模板表）
    op.drop_table('material_report_items', schema='quality')
    op.drop_table('material_reports', schema='quality')
    op.drop_table('report_templates', schema='quality')