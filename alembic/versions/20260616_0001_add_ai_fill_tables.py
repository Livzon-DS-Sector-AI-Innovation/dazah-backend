"""add AI fill tables: asset_categories, asset_page_splits, update field_mappings

Revision ID: 20260616_0001
Revises: 20260611_0003
Create Date: 2026-06-16 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '20260616_0001'
down_revision = '20260615_0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add new columns to field_mappings
    op.add_column('field_mappings',
        sa.Column('extraction_prompt', sa.Text(), nullable=True, comment='AI 提取提示'),
        schema='dossier_writer')
    op.add_column('field_mappings',
        sa.Column('source_category', sa.String(200), nullable=True, comment='素材分类名'),
        schema='dossier_writer')
    op.add_column('field_mappings',
        sa.Column('fixed_value', sa.Text(), nullable=True, comment='固定值'),
        schema='dossier_writer')
    op.add_column('field_mappings',
        sa.Column('appendix_slot', sa.String(100), nullable=True, comment='附录编号'),
        schema='dossier_writer')

    # 2. Add new columns to field_fill_results
    op.add_column('field_fill_results',
        sa.Column('ai_reasoning', sa.Text(), nullable=True, comment='AI 推理过程'),
        schema='dossier_writer')

    # 3. Create asset_categories table
    op.create_table(
        'asset_categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('chapter_code', sa.String(100), nullable=False, comment='章节编号'),
        sa.Column('category_name', sa.String(200), nullable=False, comment='分类名称'),
        sa.Column('category_type', sa.String(50), nullable=False, server_default='document', comment='分类类型'),
        sa.Column('appendix_slot', sa.String(100), nullable=True, comment='附录编号'),
        sa.Column('description', sa.Text(), nullable=True, comment='分类说明'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0', comment='排序'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.PrimaryKeyConstraint('id'),
        schema='dossier_writer'
    )

    # 4. Create asset_page_splits table
    op.create_table(
        'asset_page_splits',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('asset_id', postgresql.UUID(as_uuid=True), nullable=False, comment='素材ID'),
        sa.Column('page_number', sa.Integer(), nullable=False, comment='页码'),
        sa.Column('page_type', sa.String(200), nullable=False, comment='页面类型'),
        sa.Column('content_summary', sa.Text(), nullable=True, comment='内容摘要'),
        sa.Column('ocr_text', sa.Text(), nullable=True, comment='OCR文本'),
        sa.Column('appendix_slot', sa.String(100), nullable=True, comment='附录编号'),
        sa.Column('image_path', sa.String(500), nullable=True, comment='图片路径'),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending', comment='状态'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ['asset_id'],
            ['dossier_writer.chapter_assets.id'],
            ondelete='CASCADE'
        ),
        schema='dossier_writer'
    )


def downgrade() -> None:
    op.drop_table('asset_page_splits', schema='dossier_writer')
    op.drop_table('asset_categories', schema='dossier_writer')
    op.drop_column('field_fill_results', 'ai_reasoning', schema='dossier_writer')
    op.drop_column('field_mappings', 'appendix_slot', schema='dossier_writer')
    op.drop_column('field_mappings', 'fixed_value', schema='dossier_writer')
    op.drop_column('field_mappings', 'source_category', schema='dossier_writer')
    op.drop_column('field_mappings', 'extraction_prompt', schema='dossier_writer')
