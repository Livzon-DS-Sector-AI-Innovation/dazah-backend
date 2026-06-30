"""add dept_training_personnel table

Revision ID: f70d4b794fee
Revises: e6c93c255136
Create Date: 2026-06-30 15:35:30.754467
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'f70d4b794fee'
down_revision: Union[str, None] = 'e6c93c255136'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS hr")
    op.create_table('dept_training_personnel',
        sa.Column('id', sa.Uuid(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('display_dept', sa.String(128), nullable=True),
        sa.Column('department', sa.String(128), nullable=True),
        sa.Column('admins', sa.Text(), nullable=True),
        sa.Column('dept_head', sa.Text(), nullable=True),
        sa.Column('primary_trainer', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false')),
        schema='hr',
    )


def downgrade() -> None:
    op.drop_table('dept_training_personnel', schema='hr')
