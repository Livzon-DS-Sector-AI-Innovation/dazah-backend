"""add dossier writer field models

Revision ID: add_field_models
Revises: 68024feea3d7
Create Date: 2026-06-18
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_field_models'
down_revision: Union[str, None] = '68024feea3d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create field_mappings table
    op.create_table(
        'field_mappings',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('chapter_code', sa.String(100), nullable=False, comment='章节编号'),
        sa.Column('field_name', sa.String(200), nullable=False, comment='字段名'),
        sa.Column('field_type', sa.String(50), nullable=False, server_default='text', comment='字段类型'),
        sa.Column('location_type', sa.String(50), nullable=False, server_default='paragraph', comment='位置类型'),
        sa.Column('location_hint', sa.Text(), nullable=True, comment='位置语义提示'),
        sa.Column('extraction_prompt', sa.Text(), nullable=True, comment='AI提取提示'),
        sa.Column('source_type', sa.String(50), nullable=False, server_default='asset_extract', comment='值来源类型'),
        sa.Column('source_category', sa.String(200), nullable=True, comment='素材分类名'),
        sa.Column('fixed_value', sa.Text(), nullable=True, comment='固定值'),
        sa.Column('appendix_slot', sa.String(100), nullable=True, comment='附录编号'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0', comment='排序'),
        sa.Column('is_required', sa.Boolean(), server_default='true', nullable=False, comment='是否必填'),
        sa.PrimaryKeyConstraint('id'),
        schema='dossier_writer'
    )

    # Create field_fill_results table
    op.create_table(
        'field_fill_results',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('dossier_id', sa.UUID(), nullable=False, comment='品种资料ID'),
        sa.Column('chapter_id', sa.UUID(), nullable=False, comment='章节ID'),
        sa.Column('field_mapping_id', sa.UUID(), nullable=False, comment='字段映射ID'),
        sa.Column('field_name', sa.String(200), nullable=False, comment='字段名'),
        sa.Column('filled_value', sa.Text(), nullable=True, comment='填充的值'),
        sa.Column('source_asset_id', sa.UUID(), nullable=True, comment='来源素材ID'),
        sa.Column('source_location', sa.String(500), nullable=True, comment='素材中的位置'),
        sa.Column('fill_method', sa.String(50), nullable=False, server_default='ai', comment='填充方式'),
        sa.Column('confidence', sa.Float(), nullable=True, comment='置信度'),
        sa.Column('ai_reasoning', sa.Text(), nullable=True, comment='AI推理过程'),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending', comment='状态'),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True, comment='审核时间'),
        sa.ForeignKeyConstraint(['dossier_id'], ['dossier_writer.product_dossiers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['chapter_id'], ['dossier_writer.dossier_chapters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['field_mapping_id'], ['dossier_writer.field_mappings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_asset_id'], ['dossier_writer.chapter_assets.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        schema='dossier_writer'
    )

    # Create asset_categories table
    op.create_table(
        'asset_categories',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('chapter_code', sa.String(100), nullable=False, comment='章节编号'),
        sa.Column('category_name', sa.String(200), nullable=False, comment='分类名称'),
        sa.Column('category_type', sa.String(50), nullable=False, server_default='document', comment='分类类型'),
        sa.Column('appendix_slot', sa.String(100), nullable=True, comment='附录编号'),
        sa.Column('description', sa.Text(), nullable=True, comment='分类说明'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0', comment='排序'),
        sa.PrimaryKeyConstraint('id'),
        schema='dossier_writer'
    )

    # Create asset_page_splits table
    op.create_table(
        'asset_page_splits',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('asset_id', sa.UUID(), nullable=False, comment='素材ID'),
        sa.Column('page_number', sa.Integer(), nullable=False, comment='页码'),
        sa.Column('page_type', sa.String(200), nullable=False, comment='页面类型'),
        sa.Column('content_summary', sa.Text(), nullable=True, comment='内容摘要'),
        sa.Column('ocr_text', sa.Text(), nullable=True, comment='OCR文本'),
        sa.Column('appendix_slot', sa.String(100), nullable=True, comment='附录编号'),
        sa.Column('image_path', sa.String(500), nullable=True, comment='图片路径'),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending', comment='状态'),
        sa.ForeignKeyConstraint(['asset_id'], ['dossier_writer.chapter_assets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='dossier_writer'
    )


def downgrade() -> None:
    op.drop_table('asset_page_splits', schema='dossier_writer')
    op.drop_table('asset_categories', schema='dossier_writer')
    op.drop_table('field_fill_results', schema='dossier_writer')
    op.drop_table('field_mappings', schema='dossier_writer')
