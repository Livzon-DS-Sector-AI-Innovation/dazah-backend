"""add regulatory tracker module

Revision ID: 20260611_0002
Revises: 7d4e372b86a9, 20260606_0001
Create Date: 2026-06-11 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260611_0002'
down_revision = 'b0cec2530249'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create schema
    op.execute("CREATE SCHEMA IF NOT EXISTS regulatory_tracker")

    # Create data_sources table
    op.create_table(
        'data_sources',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(50), nullable=False, comment='数据源编码，如 CDE, NMPA'),
        sa.Column('name', sa.String(200), nullable=False, comment='数据源名称'),
        sa.Column('base_url', sa.String(500), nullable=True, comment='基础URL'),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true', comment='是否启用'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code', name='uq_data_sources_code'),
        schema='regulatory_tracker'
    )

    # Create data_channels table
    op.create_table(
        'data_channels',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source_id', postgresql.UUID(as_uuid=True), nullable=False, comment='所属数据源ID'),
        sa.Column('code', sa.String(100), nullable=False, comment='栏目编码，如 cde_domestic_guideline'),
        sa.Column('name', sa.String(200), nullable=False, comment='栏目名称'),
        sa.Column('list_url', sa.String(1000), nullable=True, comment='列表页URL'),
        sa.Column('adapter_name', sa.String(100), nullable=True, comment='适配器名称'),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true', comment='是否启用'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['source_id'], ['regulatory_tracker.data_sources.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('source_id', 'code', name='uq_data_channels_source_code'),
        schema='regulatory_tracker'
    )

    # Create regulatory_documents table
    op.create_table(
        'regulatory_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source_id', postgresql.UUID(as_uuid=True), nullable=False, comment='数据源ID'),
        sa.Column('channel_id', postgresql.UUID(as_uuid=True), nullable=False, comment='栏目ID'),
        sa.Column('document_id', sa.String(200), nullable=False, comment='文档唯一标识，如 zdyzIdCODE'),
        sa.Column('title', sa.String(1000), nullable=False, comment='标题'),
        sa.Column('publish_date', sa.Date(), nullable=True, comment='发布日期'),
        sa.Column('status_text', sa.String(100), nullable=True, comment='状态文本，如 颁布、征求意见'),
        sa.Column('classification', sa.String(200), nullable=True, comment='分类，如 生物制品、化学药品'),
        sa.Column('original_url', sa.String(1000), nullable=True, comment='原文链接'),
        sa.Column('is_new', sa.Boolean(), nullable=False, server_default='true', comment='是否新发现'),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false', comment='是否已读'),
        sa.Column('first_found_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='首次发现时间'),
        sa.Column('last_checked_at', sa.DateTime(timezone=True), nullable=True, comment='最后检查时间'),
        sa.Column('raw_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='原始JSON数据'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['source_id'], ['regulatory_tracker.data_sources.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['channel_id'], ['regulatory_tracker.data_channels.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('source_id', 'channel_id', 'document_id', name='uq_reg_docs_src_ch_doc'),
        schema='regulatory_tracker'
    )

    # Create sync_jobs table
    op.create_table(
        'sync_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source_id', postgresql.UUID(as_uuid=True), nullable=False, comment='数据源ID'),
        sa.Column('channel_id', postgresql.UUID(as_uuid=True), nullable=False, comment='栏目ID'),
        sa.Column('job_type', sa.String(50), nullable=False, comment='任务类型: backfill/daily_sync/manual_sync/test'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True, comment='开始时间'),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True, comment='结束时间'),
        sa.Column('status', sa.String(50), nullable=False, comment='状态: pending/running/success/partial_failed/failed'),
        sa.Column('total_pages', sa.Integer(), nullable=True, comment='总页数'),
        sa.Column('checked_count', sa.Integer(), nullable=False, server_default='0', comment='检查数量'),
        sa.Column('new_count', sa.Integer(), nullable=False, server_default='0', comment='新增数量'),
        sa.Column('updated_count', sa.Integer(), nullable=False, server_default='0', comment='更新数量'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='错误信息'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['source_id'], ['regulatory_tracker.data_sources.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['channel_id'], ['regulatory_tracker.data_channels.id'], ondelete='CASCADE'),
        schema='regulatory_tracker'
    )

    # Create sync_job_pages table
    op.create_table(
        'sync_job_pages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sync_job_id', postgresql.UUID(as_uuid=True), nullable=False, comment='同步任务ID'),
        sa.Column('page_number', sa.Integer(), nullable=False, comment='页码'),
        sa.Column('page_size', sa.Integer(), nullable=False, server_default='10', comment='每页条数'),
        sa.Column('total_records_on_page', sa.Integer(), nullable=False, server_default='0', comment='本页记录数'),
        sa.Column('new_records', sa.Integer(), nullable=False, server_default='0', comment='本页新增记录数'),
        sa.Column('status', sa.String(50), nullable=False, comment='状态: pending/synced/failed'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True, comment='开始时间'),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True, comment='结束时间'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='错误信息'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['sync_job_id'], ['regulatory_tracker.sync_jobs.id'], ondelete='CASCADE'),
        schema='regulatory_tracker'
    )

    # Create indexes
    op.create_index('ix_regulatory_documents_publish_date', 'regulatory_documents', ['publish_date'], schema='regulatory_tracker')
    op.create_index('ix_regulatory_documents_is_new', 'regulatory_documents', ['is_new'], schema='regulatory_tracker')
    op.create_index('ix_regulatory_documents_is_read', 'regulatory_documents', ['is_read'], schema='regulatory_tracker')
    op.create_index('ix_sync_jobs_status', 'sync_jobs', ['status'], schema='regulatory_tracker')
    op.create_index('ix_sync_job_pages_page_number', 'sync_job_pages', ['page_number'], schema='regulatory_tracker')
    op.create_index('ix_sync_job_pages_status', 'sync_job_pages', ['status'], schema='regulatory_tracker')


def downgrade() -> None:
    op.drop_index('ix_sync_job_pages_status', table_name='sync_job_pages', schema='regulatory_tracker')
    op.drop_index('ix_sync_job_pages_page_number', table_name='sync_job_pages', schema='regulatory_tracker')
    op.drop_index('ix_sync_jobs_status', table_name='sync_jobs', schema='regulatory_tracker')
    op.drop_index('ix_regulatory_documents_is_read', table_name='regulatory_documents', schema='regulatory_tracker')
    op.drop_index('ix_regulatory_documents_is_new', table_name='regulatory_documents', schema='regulatory_tracker')
    op.drop_index('ix_regulatory_documents_publish_date', table_name='regulatory_documents', schema='regulatory_tracker')
    
    op.drop_table('sync_job_pages', schema='regulatory_tracker')
    op.drop_table('sync_jobs', schema='regulatory_tracker')
    op.drop_table('regulatory_documents', schema='regulatory_tracker')
    op.drop_table('data_channels', schema='regulatory_tracker')
    op.drop_table('data_sources', schema='regulatory_tracker')
    
    op.execute("DROP SCHEMA IF EXISTS regulatory_tracker CASCADE")
