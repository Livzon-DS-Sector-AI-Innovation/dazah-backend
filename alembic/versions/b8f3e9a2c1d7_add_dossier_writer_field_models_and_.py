"""add dossier writer field models and equipment person fields

Revision ID: b8f3e9a2c1d7
Revises: 68024feea3d7
Create Date: 2026-06-18 11:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b8f3e9a2c1d7'
down_revision: Union[str, None] = '68024feea3d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create dossier_writer field model tables
    op.create_table(
        'field_mappings',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('chapter_code', sa.String(length=100), nullable=False, comment='章节编号，如 3.2.S.6'),
        sa.Column('field_name', sa.String(length=200), nullable=False, comment='字段名，如 包材类型'),
        sa.Column('field_type', sa.String(length=50), nullable=False, server_default='text', comment='字段类型: text/table/image_appendix'),
        sa.Column('location_type', sa.String(length=50), nullable=False, server_default='paragraph', comment='模板中的位置类型: paragraph/table/appendix/inline_image'),
        sa.Column('location_hint', sa.Text(), nullable=True, comment='位置语义提示'),
        sa.Column('extraction_prompt', sa.Text(), nullable=True, comment='AI 提取提示'),
        sa.Column('source_type', sa.String(length=50), nullable=False, server_default='asset_extract', comment='值来源类型'),
        sa.Column('source_category', sa.String(length=200), nullable=True, comment='素材分类名'),
        sa.Column('fixed_value', sa.Text(), nullable=True, comment='固定值'),
        sa.Column('appendix_slot', sa.String(length=100), nullable=True, comment='附录编号'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0', comment='字段在章节内的排序'),
        sa.Column('is_required', sa.Boolean(), server_default='true', nullable=False, comment='是否必填'),
        sa.PrimaryKeyConstraint('id'),
        schema='dossier_writer'
    )
    
    op.create_table(
        'field_fill_results',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('dossier_id', sa.Uuid(), nullable=False, comment='品种资料ID'),
        sa.Column('chapter_id', sa.Uuid(), nullable=False, comment='章节ID'),
        sa.Column('field_mapping_id', sa.Uuid(), nullable=False, comment='字段映射ID'),
        sa.Column('field_name', sa.String(length=200), nullable=False, comment='字段名（冗余存储便于查询）'),
        sa.Column('filled_value', sa.Text(), nullable=True, comment='填充的值'),
        sa.Column('source_asset_id', sa.Uuid(), nullable=True, comment='值来自哪个素材文件'),
        sa.Column('source_location', sa.String(length=500), nullable=True, comment='在素材中的位置'),
        sa.Column('fill_method', sa.String(length=50), nullable=False, server_default='ai', comment='填充方式: ai/rule/manual'),
        sa.Column('confidence', sa.Float(), nullable=True, comment='置信度（AI填充时用，0-1）'),
        sa.Column('ai_reasoning', sa.Text(), nullable=True, comment='AI 的推理过程，用于用户审核'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending', comment='状态: pending/extracted/filled/reviewed/rejected'),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True, comment='审核时间'),
        sa.ForeignKeyConstraint(['dossier_id'], ['dossier_writer.product_dossiers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['chapter_id'], ['dossier_writer.dossier_chapters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['field_mapping_id'], ['dossier_writer.field_mappings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_asset_id'], ['dossier_writer.chapter_assets.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        schema='dossier_writer'
    )
    
    op.create_table(
        'asset_categories',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('chapter_code', sa.String(length=100), nullable=False, comment='章节编号，如 3.2.S.6'),
        sa.Column('category_name', sa.String(length=200), nullable=False, comment='分类名称，如 授权书'),
        sa.Column('category_type', sa.String(length=50), nullable=False, server_default='document', comment='分类类型: document/image_appendix/both'),
        sa.Column('appendix_slot', sa.String(length=100), nullable=True, comment='对应模板中的附录编号'),
        sa.Column('description', sa.Text(), nullable=True, comment='分类说明'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0', comment='排序序号'),
        sa.PrimaryKeyConstraint('id'),
        schema='dossier_writer'
    )
    
    op.create_table(
        'asset_page_splits',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('asset_id', sa.Uuid(), nullable=False, comment='素材ID'),
        sa.Column('page_number', sa.Integer(), nullable=False, comment='页码（从1开始）'),
        sa.Column('page_type', sa.String(length=200), nullable=False, comment='AI 识别的页面类型'),
        sa.Column('content_summary', sa.Text(), nullable=True, comment='页面内容摘要'),
        sa.Column('ocr_text', sa.Text(), nullable=True, comment='OCR 提取的页面文本'),
        sa.Column('appendix_slot', sa.String(length=100), nullable=True, comment='用户确认的附录编号'),
        sa.Column('image_path', sa.String(length=500), nullable=True, comment='转换后的图片路径'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending', comment='状态: pending/confirmed/inserted/skipped'),
        sa.ForeignKeyConstraint(['asset_id'], ['dossier_writer.chapter_assets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='dossier_writer'
    )
    
    # Add equipment.equipments columns
    op.add_column('equipments', sa.Column('department_id', sa.Uuid(), nullable=True, comment='归属部门ID，逻辑引用 identity.departments.id'), schema='equipment')
    op.add_column('equipments', sa.Column('responsible_person_id', sa.Uuid(), nullable=True, comment='负责人ID，逻辑引用 identity.users.id；未设置时由部门负责人推导'), schema='equipment')


def downgrade() -> None:
    # Remove equipment.equipments columns
    op.drop_column('equipments', 'responsible_person_id', schema='equipment')
    op.drop_column('equipments', 'department_id', schema='equipment')
    
    # Drop dossier_writer field model tables
    op.drop_table('asset_page_splits', schema='dossier_writer')
    op.drop_table('asset_categories', schema='dossier_writer')
    op.drop_table('field_fill_results', schema='dossier_writer')
    op.drop_table('field_mappings', schema='dossier_writer')
