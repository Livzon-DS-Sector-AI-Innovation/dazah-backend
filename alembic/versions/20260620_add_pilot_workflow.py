"""add pilot workflow tables

Revision ID: a1b2c3d4e5f6
Revises: fd513f53016e
Create Date: 2026-06-20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'e4f5a6b7c8d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'pilot_workflows',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('project_id', sa.String(50), nullable=True),
        sa.Column('product_name', sa.String(200), nullable=False),
        sa.Column('scale_up_ratio', sa.Float(), nullable=False, server_default='10.0'),
        sa.Column('equipment_type', sa.String(100), nullable=False),
        sa.Column('equipment_volume', sa.Float(), nullable=False),
        sa.Column('input_document_path', sa.String(500), nullable=True),
        sa.Column('input_context', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('final_report', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        schema='research',
    )

    op.create_table(
        'pilot_workflow_steps',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('workflow_id', sa.String(50), nullable=False),
        sa.Column('step_order', sa.Integer(), nullable=False),
        sa.Column('step_code', sa.String(50), nullable=False),
        sa.Column('step_name', sa.String(200), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('input_data', sa.JSON(), nullable=True),
        sa.Column('output_data', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        schema='research',
    )


def downgrade() -> None:
    op.drop_table('pilot_workflow_steps', schema='research')
    op.drop_table('pilot_workflows', schema='research')
