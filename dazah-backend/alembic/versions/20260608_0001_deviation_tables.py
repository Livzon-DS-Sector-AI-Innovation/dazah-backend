"""偏差管理模块数据库迁移

Revision ID: dev_001
Revises: 20260604_0003
Create Date: 2026-06-08
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'dev_001'
down_revision = '20260604_0003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建枚举类型
    deviation_type_enum = postgresql.ENUM(
        'production', 'inspection', 'equipment', 'environment', 'warehouse', 'personnel',
        name='deviation_type_enum', create_type=False
    )
    deviation_type_enum.create(op.get_bind(), checkfirst=True)

    deviation_level_enum = postgresql.ENUM(
        'critical', 'major', 'minor',
        name='deviation_level_enum', create_type=False
    )
    deviation_level_enum.create(op.get_bind(), checkfirst=True)

    deviation_status_enum = postgresql.ENUM(
        'draft', 'submitted', 'admin_approved', 'qa_approved', 'quality_approved',
        'active', 'investigating', 'investigation_completed', 'correction_pending',
        'correction_in_progress', 'correction_completed', 'closing_pending', 'closed', 'rejected',
        name='deviation_status_enum', create_type=False
    )
    deviation_status_enum.create(op.get_bind(), checkfirst=True)

    investigation_status_enum = postgresql.ENUM(
        'pending', 'in_progress', 'completed',
        name='investigation_status_enum', create_type=False
    )
    investigation_status_enum.create(op.get_bind(), checkfirst=True)

    correction_status_enum = postgresql.ENUM(
        'pending', 'in_progress', 'completed',
        name='correction_status_enum', create_type=False
    )
    correction_status_enum.create(op.get_bind(), checkfirst=True)

    # 创建偏差主表
    op.create_table(
        'quality_deviations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deviation_no', sa.String(length=64), nullable=False),
        sa.Column('occurrence_date', sa.DateTime(), nullable=True),
        sa.Column('discovering_department', sa.String(length=100), nullable=True),
        sa.Column('discoverer', sa.String(length=100), nullable=True),
        sa.Column('product_code', sa.String(length=64), nullable=True),
        sa.Column('product_name', sa.String(length=255), nullable=True),
        sa.Column('production_batch', sa.String(length=64), nullable=True),
        sa.Column('material_code', sa.String(length=64), nullable=True),
        sa.Column('batch_size', sa.String(length=64), nullable=True),
        sa.Column('deviation_type', deviation_type_enum, nullable=False),
        sa.Column('deviation_level', deviation_level_enum, nullable=False),
        sa.Column('abnormal_description', sa.Text(), nullable=True),
        sa.Column('impact_scope', sa.Text(), nullable=True),
        sa.Column('emergency_measures', sa.Text(), nullable=True),
        sa.Column('attachments', postgresql.JSONB(), nullable=True),
        sa.Column('batch_locked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('batch_lock_reason', sa.Text(), nullable=True),
        sa.Column('batch_locked_at', sa.DateTime(), nullable=True),
        sa.Column('status', deviation_status_enum, nullable=False, server_default='draft'),
        schema='quality'
    )
    op.create_index('idx_deviation_no', 'quality_deviations', ['deviation_no'], unique=True, schema='quality')
    op.create_index('idx_deviation_status', 'quality_deviations', ['status'], schema='quality')
    op.create_index('idx_deviation_type', 'quality_deviations', ['deviation_type'], schema='quality')
    op.create_index('idx_deviation_level', 'quality_deviations', ['deviation_level'], schema='quality')
    op.create_index('idx_occurrence_date', 'quality_deviations', ['occurrence_date'], schema='quality')

    # 创建偏差调查表
    op.create_table(
        'quality_deviation_investigations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deviation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('investigation_team', sa.String(length=255), nullable=True),
        sa.Column('investigation_start_date', sa.DateTime(), nullable=True),
        sa.Column('investigation_end_date', sa.DateTime(), nullable=True),
        sa.Column('investigation_method', sa.String(length=100), nullable=True),
        sa.Column('direct_cause', sa.Text(), nullable=True),
        sa.Column('indirect_cause', sa.Text(), nullable=True),
        sa.Column('root_cause', sa.Text(), nullable=True),
        sa.Column('why_analysis', sa.Text(), nullable=True),
        sa.Column('impact_assessment', sa.Text(), nullable=True),
        sa.Column('affected_batches', sa.Text(), nullable=True),
        sa.Column('temporary_measures', sa.Text(), nullable=True),
        sa.Column('attachments', postgresql.JSONB(), nullable=True),
        sa.Column('status', investigation_status_enum, nullable=False, server_default='pending'),
        schema='quality'
    )
    op.create_index('idx_investigation_deviation', 'quality_deviation_investigations', ['deviation_id'], schema='quality')

    # 创建偏差整改表
    op.create_table(
        'quality_deviation_corrections',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deviation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('responsible_department', sa.String(length=100), nullable=True),
        sa.Column('responsible_person', sa.String(length=100), nullable=True),
        sa.Column('plan_completion_date', sa.DateTime(), nullable=True),
        sa.Column('temporary_corrective_actions', postgresql.JSONB(), nullable=True),
        sa.Column('long_term_corrective_actions', postgresql.JSONB(), nullable=True),
        sa.Column('progress', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', correction_status_enum, nullable=False, server_default='pending'),
        sa.Column('evidence_attachments', postgresql.JSONB(), nullable=True),
        schema='quality'
    )
    op.create_index('idx_correction_deviation', 'quality_deviation_corrections', ['deviation_id'], schema='quality')

    # 创建偏差关闭表
    op.create_table(
        'quality_deviation_closings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deviation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('verification_plan', sa.Text(), nullable=True),
        sa.Column('verification_data', sa.Text(), nullable=True),
        sa.Column('verification_result', sa.Text(), nullable=True),
        sa.Column('is_resolved', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('conclusion', sa.Text(), nullable=True),
        sa.Column('attachments', postgresql.JSONB(), nullable=True),
        sa.Column('batch_unlocked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('archived', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('archived_at', sa.DateTime(), nullable=True),
        schema='quality'
    )
    op.create_index('idx_closing_deviation', 'quality_deviation_closings', ['deviation_id'], schema='quality')

    # 创建偏差审批记录表
    op.create_table(
        'quality_deviation_approvals',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deviation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('approval_type', sa.String(length=50), nullable=False),
        sa.Column('approver_name', sa.String(length=100), nullable=True),
        sa.Column('approver_department', sa.String(length=100), nullable=True),
        sa.Column('approval_comments', sa.Text(), nullable=True),
        sa.Column('approved', sa.Boolean(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        schema='quality'
    )
    op.create_index('idx_approval_deviation', 'quality_deviation_approvals', ['deviation_id'], schema='quality')

    # 添加外键约束
    op.create_foreign_key(
        'fk_investigation_deviation',
        'quality_deviation_investigations', 'quality_deviations',
        ['deviation_id'], ['id'],
        source_schema='quality', referent_schema='quality'
    )
    op.create_foreign_key(
        'fk_correction_deviation',
        'quality_deviation_corrections', 'quality_deviations',
        ['deviation_id'], ['id'],
        source_schema='quality', referent_schema='quality'
    )
    op.create_foreign_key(
        'fk_closing_deviation',
        'quality_deviation_closings', 'quality_deviations',
        ['deviation_id'], ['id'],
        source_schema='quality', referent_schema='quality'
    )
    op.create_foreign_key(
        'fk_approval_deviation',
        'quality_deviation_approvals', 'quality_deviations',
        ['deviation_id'], ['id'],
        source_schema='quality', referent_schema='quality'
    )


def downgrade() -> None:
    # 删除外键约束
    op.drop_constraint('fk_approval_deviation', 'quality_deviation_approvals', 'foreignkey', schema='quality')
    op.drop_constraint('fk_closing_deviation', 'quality_deviation_closings', 'foreignkey', schema='quality')
    op.drop_constraint('fk_correction_deviation', 'quality_deviation_corrections', 'foreignkey', schema='quality')
    op.drop_constraint('fk_investigation_deviation', 'quality_deviation_investigations', 'foreignkey', schema='quality')

    # 删除表
    op.drop_table('quality_deviation_approvals', schema='quality')
    op.drop_table('quality_deviation_closings', schema='quality')
    op.drop_table('quality_deviation_corrections', schema='quality')
    op.drop_table('quality_deviation_investigations', schema='quality')
    op.drop_table('quality_deviations', schema='quality')

    # 删除枚举类型
    op.execute('DROP TYPE IF EXISTS deviation_status_enum')
    op.execute('DROP TYPE IF EXISTS deviation_level_enum')
    op.execute('DROP TYPE IF EXISTS deviation_type_enum')
    op.execute('DROP TYPE IF EXISTS investigation_status_enum')
    op.execute('DROP TYPE IF EXISTS correction_status_enum')