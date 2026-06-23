"""add route developments tables

Revision ID: e4f5a6b7c8d9
Revises: 03a39fa728a5
Create Date: 2026-06-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision = 'e4f5a6b7c8d9'
down_revision = '03a39fa728a5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    from sqlalchemy import inspect, text
    conn = op.get_bind()
    
    # Check if tables already exist
    inspector = inspect(conn)
    existing_tables = inspector.get_table_names(schema='research')
    
    if 'route_developments' not in existing_tables:
        op.create_table(
        'route_developments',
        sa.Column('project_id', sa.String(50), nullable=False, comment='所属研发项目ID'),
        sa.Column('route_no', sa.String(50), nullable=False, comment='路线编号'),
        sa.Column('name', sa.String(200), nullable=False, comment='路线名称'),
        sa.Column('source', sa.String(50), nullable=False, server_default='manual', comment='来源: manual/literature/llm'),
        sa.Column('source_reference', sa.String(500), nullable=True, comment='来源引用'),
        sa.Column('description', sa.Text(), nullable=True, comment='描述'),
        sa.Column('status', sa.String(20), nullable=False, server_default='planning', comment='状态: planning/in_progress/completed/failed'),
        sa.Column('current_module', sa.String(20), nullable=False, server_default='research', comment='当前工作流阶段'),
        sa.Column('literature_sources', sa.JSON(), nullable=True, comment='文献来源数据'),
        sa.Column('candidate_routes', sa.JSON(), nullable=True, comment='候选路线列表'),
        sa.Column('selected_route_ids', sa.JSON(), nullable=True, comment='已选路线ID列表'),
        sa.Column('experiment_plans', sa.JSON(), nullable=True, comment='实验方案列表'),
        sa.Column('assessment', sa.JSON(), nullable=True, comment='四维度评估结果'),
        sa.Column('deliverables', sa.JSON(), nullable=True, comment='交付物列表'),
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

    if 'route_experiments' not in existing_tables:
        op.create_table(
                'route_experiments',
            sa.Column('route_id', sa.String(50), nullable=False, comment='所属路线ID'),
            sa.Column('experiment_no', sa.String(50), nullable=False, comment='实验编号'),
            sa.Column('title', sa.String(200), nullable=False, comment='实验标题'),
            sa.Column('description', sa.Text(), nullable=True, comment='实验描述'),
            sa.Column('experiment_date', sa.Date(), nullable=True, comment='实验日期'),
            sa.Column('operator', sa.String(100), nullable=True, comment='操作人'),
            sa.Column('status', sa.String(20), nullable=False, server_default='planned', comment='状态: planned/in_progress/completed/failed'),
            sa.Column('reaction_temp', sa.String(100), nullable=True, comment='反应温度'),
            sa.Column('reaction_time', sa.String(100), nullable=True, comment='反应时间'),
            sa.Column('yield_pct', sa.Float(), nullable=True, comment='收率(%)'),
            sa.Column('purity', sa.Float(), nullable=True, comment='纯度(%)'),
            sa.Column('impurities', sa.Float(), nullable=True, comment='杂质(%)'),
            sa.Column('result_summary', sa.Text(), nullable=True, comment='结果摘要'),
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
        op.drop_table('route_experiments', schema='research')
        op.drop_table('route_developments', schema='research')
    