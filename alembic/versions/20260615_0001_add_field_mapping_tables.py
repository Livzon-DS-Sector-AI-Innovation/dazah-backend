"""add field mapping tables

Revision ID: 20260615_0001
Revises: 20260611_0004
Create Date: 2026-06-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '20260615_0001'
down_revision = '20260611_0004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 字段映射配置表
    op.create_table(
        'field_mappings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('chapter_code', sa.String(100), nullable=False, comment='章节编号'),
        sa.Column('field_name', sa.String(200), nullable=False, comment='字段名'),
        sa.Column('field_type', sa.String(50), nullable=False, server_default='text', comment='字段类型'),
        sa.Column('location_type', sa.String(50), nullable=False, server_default='paragraph', comment='位置类型'),
        sa.Column('location_hint', sa.Text, nullable=True, comment='位置提示'),
        sa.Column('extraction_rule', sa.Text, nullable=True, comment='提取规则'),
        sa.Column('source_type', sa.String(50), nullable=False, server_default='asset_file', comment='值来源类型'),
        sa.Column('source_pattern', sa.String(500), nullable=True, comment='素材文件名匹配规则'),
        sa.Column('sort_order', sa.Integer, nullable=False, server_default='0', comment='排序'),
        sa.Column('is_required', sa.Boolean, nullable=False, server_default='true', comment='是否必填'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean, nullable=False, server_default='false'),
        schema='dossier_writer'
    )
    
    # 字段填充结果表
    op.create_table(
        'field_fill_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('dossier_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('chapter_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('field_mapping_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('field_name', sa.String(200), nullable=False, comment='字段名'),
        sa.Column('filled_value', sa.Text, nullable=True, comment='填充的值'),
        sa.Column('source_asset_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('source_location', sa.String(500), nullable=True, comment='素材中的位置'),
        sa.Column('fill_method', sa.String(50), nullable=False, server_default='rule', comment='填充方式'),
        sa.Column('confidence', sa.Float, nullable=True, comment='置信度'),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending', comment='状态'),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean, nullable=False, server_default='false'),
        sa.ForeignKeyConstraint(['dossier_id'], ['dossier_writer.product_dossiers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['chapter_id'], ['dossier_writer.dossier_chapters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['field_mapping_id'], ['dossier_writer.field_mappings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_asset_id'], ['dossier_writer.chapter_assets.id'], ondelete='SET NULL'),
        schema='dossier_writer'
    )
    
    # 创建索引
    op.create_index('ix_field_mappings_chapter_code', 'field_mappings', ['chapter_code'], schema='dossier_writer')
    op.create_index('ix_field_fill_results_dossier_id', 'field_fill_results', ['dossier_id'], schema='dossier_writer')
    op.create_index('ix_field_fill_results_chapter_id', 'field_fill_results', ['chapter_id'], schema='dossier_writer')


def downgrade() -> None:
    op.drop_index('ix_field_fill_results_chapter_id', table_name='field_fill_results', schema='dossier_writer')
    op.drop_index('ix_field_fill_results_dossier_id', table_name='field_fill_results', schema='dossier_writer')
    op.drop_index('ix_field_mappings_chapter_code', table_name='field_mappings', schema='dossier_writer')
    op.drop_table('field_fill_results', schema='dossier_writer')
    op.drop_table('field_mappings', schema='dossier_writer')
