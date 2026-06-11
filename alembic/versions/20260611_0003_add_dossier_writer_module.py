"""add dossier writer module

Revision ID: 20260611_0003
Revises: 20260611_0002
Create Date: 2026-06-11 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260611_0003'
down_revision = '20260611_0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create schema
    op.execute("CREATE SCHEMA IF NOT EXISTS dossier_writer")

    # Create product_dossiers table
    op.create_table(
        'product_dossiers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_name', sa.String(200), nullable=False, comment='品种名称'),
        sa.Column('sterile_type', sa.String(50), nullable=False, comment='无菌/非无菌'),
        sa.Column('manufacturer', sa.String(300), nullable=False, comment='生产商'),
        sa.Column('template_original_product_name', sa.String(200), nullable=True, comment='模板原品种名称'),
        sa.Column('template_original_manufacturer', sa.String(300), nullable=True, comment='模板原生产商'),
        sa.Column('source_templates_path', sa.String(500), nullable=True, comment='原始模板目录路径'),
        sa.Column('working_path', sa.String(500), nullable=True, comment='工作副本目录路径'),
        sa.Column('assets_path', sa.String(500), nullable=True, comment='素材目录路径'),
        sa.Column('outputs_path', sa.String(500), nullable=True, comment='导出目录路径'),
        sa.Column('status', sa.String(50), server_default='draft', comment='状态: draft/parsing/completed'),
        sa.Column('parse_status', sa.String(50), server_default='pending', comment='解析状态: pending/parsing/completed/failed'),
        sa.Column('parse_error', sa.Text(), nullable=True, comment='解析错误信息'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.PrimaryKeyConstraint('id'),
        schema='dossier_writer'
    )

    # Create dossier_templates table
    op.create_table(
        'dossier_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_dossier_id', postgresql.UUID(as_uuid=True), nullable=False, comment='品种资料ID'),
        sa.Column('original_filename', sa.String(300), nullable=False, comment='原始文件名'),
        sa.Column('file_path', sa.String(500), nullable=False, comment='文件存储路径'),
        sa.Column('file_size', sa.Integer(), nullable=True, comment='文件大小(字节)'),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ['product_dossier_id'],
            ['dossier_writer.product_dossiers.id'],
            ondelete='CASCADE'
        ),
        schema='dossier_writer'
    )

    # Create dossier_chapters table
    op.create_table(
        'dossier_chapters',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_dossier_id', postgresql.UUID(as_uuid=True), nullable=False, comment='品种资料ID'),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True, comment='父章节ID'),
        sa.Column('chapter_code', sa.String(100), nullable=True, comment='章节编号'),
        sa.Column('chapter_title', sa.String(500), nullable=False, comment='章节标题'),
        sa.Column('level', sa.Integer(), nullable=False, server_default='1', comment='层级深度'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0', comment='排序序号'),
        sa.Column('source_file', sa.String(500), nullable=True, comment='源模板文件名'),
        sa.Column('working_file', sa.String(500), nullable=True, comment='工作副本文件名'),
        sa.Column('paragraph_start', sa.Integer(), nullable=True, comment='起始段落索引'),
        sa.Column('paragraph_end', sa.Integer(), nullable=True, comment='结束段落索引'),
        sa.Column('has_content', sa.Boolean(), server_default='false', comment='是否有内容'),
        sa.Column('has_assets', sa.Boolean(), server_default='false', comment='是否有素材'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ['product_dossier_id'],
            ['dossier_writer.product_dossiers.id'],
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['parent_id'],
            ['dossier_writer.dossier_chapters.id'],
            ondelete='CASCADE'
        ),
        schema='dossier_writer'
    )

    # Create chapter_assets table
    op.create_table(
        'chapter_assets',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('chapter_id', postgresql.UUID(as_uuid=True), nullable=False, comment='章节ID'),
        sa.Column('original_filename', sa.String(300), nullable=False, comment='原始文件名'),
        sa.Column('file_path', sa.String(500), nullable=False, comment='文件存储路径'),
        sa.Column('file_type', sa.String(50), nullable=True, comment='文件类型'),
        sa.Column('file_size', sa.Integer(), nullable=True, comment='文件大小(字节)'),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ['chapter_id'],
            ['dossier_writer.dossier_chapters.id'],
            ondelete='CASCADE'
        ),
        schema='dossier_writer'
    )

    # Create indexes
    op.create_index('ix_product_dossiers_is_deleted', 'product_dossiers', ['is_deleted'], schema='dossier_writer')
    op.create_index('ix_dossier_templates_product_dossier_id', 'dossier_templates', ['product_dossier_id'], schema='dossier_writer')
    op.create_index('ix_dossier_chapters_product_dossier_id', 'dossier_chapters', ['product_dossier_id'], schema='dossier_writer')
    op.create_index('ix_dossier_chapters_parent_id', 'dossier_chapters', ['parent_id'], schema='dossier_writer')
    op.create_index('ix_chapter_assets_chapter_id', 'chapter_assets', ['chapter_id'], schema='dossier_writer')


def downgrade() -> None:
    op.drop_index('ix_chapter_assets_chapter_id', table_name='chapter_assets', schema='dossier_writer')
    op.drop_index('ix_dossier_chapters_parent_id', table_name='dossier_chapters', schema='dossier_writer')
    op.drop_index('ix_dossier_chapters_product_dossier_id', table_name='dossier_chapters', schema='dossier_writer')
    op.drop_index('ix_dossier_templates_product_dossier_id', table_name='dossier_templates', schema='dossier_writer')
    op.drop_index('ix_product_dossiers_is_deleted', table_name='product_dossiers', schema='dossier_writer')
    
    op.drop_table('chapter_assets', schema='dossier_writer')
    op.drop_table('dossier_chapters', schema='dossier_writer')
    op.drop_table('dossier_templates', schema='dossier_writer')
    op.drop_table('product_dossiers', schema='dossier_writer')
    
    op.execute("DROP SCHEMA IF EXISTS dossier_writer")
