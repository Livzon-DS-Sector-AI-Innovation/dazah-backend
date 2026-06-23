"""add process optimizations table

Revision ID: cdfd8d9991b4
Revises: 190bbff9dc50
Create Date: 2026-06-20 00:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cdfd8d9991b4'
down_revision = '190bbff9dc50'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'process_optimizations',
        sa.Column('project_id', sa.String(50), nullable=False, comment='所属研发项目ID'),
        sa.Column('optimization_no', sa.String(50), nullable=False, comment='优化编号'),
        sa.Column('name', sa.String(200), nullable=False, comment='优化任务名称'),
        sa.Column('source_route_id', sa.String(50), nullable=True, comment='来源路线ID'),
        sa.Column('source_route_name', sa.String(200), nullable=True, comment='来源路线名称'),
        sa.Column('description', sa.Text(), nullable=True, comment='描述'),
        sa.Column('status', sa.String(20), nullable=False, server_default='planning', comment='状态: planning/in_progress/completed/failed'),
        sa.Column('current_module', sa.String(20), nullable=False, server_default='doe', comment='当前工作流阶段: doe/impurity/crystal/quality/scaleup/report'),
        sa.Column('doe_experiment', sa.JSON(), nullable=True, comment='DOE实验设计与分析数据'),
        sa.Column('impurity_study', sa.JSON(), nullable=True, comment='杂质研究数据'),
        sa.Column('crystal_form_study', sa.JSON(), nullable=True, comment='晶型研究数据'),
        sa.Column('quality_standard_set', sa.JSON(), nullable=True, comment='质量标准数据'),
        sa.Column('scale_up_study', sa.JSON(), nullable=True, comment='公斤级放大数据'),
        sa.Column('start_date', sa.Date(), nullable=True, comment='开始日期'),
        sa.Column('end_date', sa.Date(), nullable=True, comment='结束日期'),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['identity.users.id']),
        sa.ForeignKeyConstraint(['updated_by'], ['identity.users.id']),
        schema='research'
    )


def downgrade() -> None:
    op.drop_table('process_optimizations', schema='research')
