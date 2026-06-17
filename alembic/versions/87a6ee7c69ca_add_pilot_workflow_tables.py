"""add pilot workflow tables

Revision ID: 87a6ee7c69ca
Revises: b9326d0ec97b
Create Date: 2026-06-16 19:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '87a6ee7c69ca'
down_revision: Union[str, None] = 'b9326d0ec97b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create research.pilot_workflows table
    op.execute("CREATE SCHEMA IF NOT EXISTS research")

    op.create_table(
        'pilot_workflows',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=True,
                  comment='关联研发项目ID'),
        sa.Column('product_name', sa.String(200), nullable=False,
                  comment='产品名称'),
        sa.Column('scale_up_ratio', sa.Float(), nullable=False,
                  comment='放大倍数'),
        sa.Column('equipment_type', sa.String(100), nullable=False,
                  comment='设备类型'),
        sa.Column('equipment_volume', sa.Float(), nullable=False,
                  comment='设备容积(L)'),
        sa.Column('input_document_path', sa.String(500), nullable=True,
                  comment='上传文档路径'),
        sa.Column('input_context', postgresql.JSON(), nullable=True,
                  comment='额外上下文'),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending',
                  comment='状态'),
        sa.Column('final_report', postgresql.JSON(), nullable=True,
                  comment='最终报告'),
        # BaseModel fields
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.CheckConstraint(
            "status IN ('pending', 'running', 'completed', 'failed')",
            name='ck_pilot_workflows_status',
        ),
        schema='research',
    )

    # Create research.pilot_workflow_steps table
    op.create_table(
        'pilot_workflow_steps',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('workflow_id', postgresql.UUID(as_uuid=True), nullable=False,
                  comment='工作流ID'),
        sa.Column('step_order', sa.Integer(), nullable=False,
                  comment='步骤序号'),
        sa.Column('step_code', sa.String(50), nullable=False,
                  comment='步骤标识'),
        sa.Column('step_name', sa.String(100), nullable=False,
                  comment='步骤名称'),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending',
                  comment='状态'),
        sa.Column('input_data', postgresql.JSON(), nullable=True,
                  comment='输入数据'),
        sa.Column('output_data', postgresql.JSON(), nullable=True,
                  comment='输出数据'),
        sa.Column('error_message', sa.Text(), nullable=True,
                  comment='错误信息'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True,
                  comment='开始时间'),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True,
                  comment='完成时间'),
        # BaseModel fields
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.CheckConstraint(
            "status IN ('pending', 'running', 'completed', 'failed', 'skipped')",
            name='ck_pilot_workflow_steps_status',
        ),
        schema='research',
    )

    # Add indexes
    op.create_index('ix_pilot_workflows_status', 'pilot_workflows', ['status'], schema='research')
    op.create_index('ix_pilot_workflow_steps_workflow_id', 'pilot_workflow_steps', ['workflow_id'], schema='research')
    op.create_index('ix_pilot_workflow_steps_step_order', 'pilot_workflow_steps', ['step_order'], schema='research')


def downgrade() -> None:
    op.drop_table('pilot_workflow_steps', schema='research')
    op.drop_table('pilot_workflows', schema='research')
