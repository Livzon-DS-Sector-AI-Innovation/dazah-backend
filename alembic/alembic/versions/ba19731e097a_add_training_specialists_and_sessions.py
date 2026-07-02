"""add_training_specialists_and_sessions

Revision ID: ba19731e097a
Revises: xbj3_final_001
Create Date: 2026-06-24 09:25:23.055876
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = 'ba19731e097a'
down_revision: Union[str, None] = 'xbj3_final_001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'training_sessions',
        sa.Column('factory', sa.String(length=8), server_default='old', nullable=False),
        sa.Column('department', sa.String(length=64), nullable=False),
        sa.Column('training_date', sa.Date(), nullable=False),
        sa.Column('subject', sa.String(length=256), nullable=False),
        sa.Column('training_time_start', sa.String(length=32), nullable=True),
        sa.Column('training_time_end', sa.String(length=32), nullable=True),
        sa.Column('location', sa.String(length=128), nullable=True),
        sa.Column('trainer', sa.String(length=128), nullable=True),
        sa.Column('training_method', sa.String(length=32), nullable=True),
        sa.Column('content', sa.String(length=512), nullable=True),
        sa.Column('trainee_departments', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('employee_names', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('employee_numbers', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('issuer_department', sa.String(length=64), nullable=True),
        sa.Column('issue_date', sa.Date(), nullable=True),
        sa.Column('remarks', sa.String(length=512), nullable=True),
        sa.Column('status', sa.String(length=16), server_default='draft', nullable=False),
        sa.Column('select_task_token', sa.String(length=64), nullable=True),
        sa.Column('select_tasks', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['identity.users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['identity.users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='hr'
    )
    op.create_index('ix_training_sessions_department', 'training_sessions', ['department'], unique=False, schema='hr')
    op.create_index('ix_training_sessions_training_date', 'training_sessions', ['training_date'], unique=False, schema='hr')
    op.create_index('ix_training_sessions_status', 'training_sessions', ['status'], unique=False, schema='hr')

    op.create_table(
        'training_specialists',
        sa.Column('department', sa.String(length=64), nullable=False),
        sa.Column('employee_number', sa.String(length=32), nullable=False),
        sa.Column('employee_name', sa.String(length=64), nullable=False),
        sa.Column('factory', sa.String(length=8), server_default='old', nullable=False),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['identity.users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['identity.users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='hr'
    )
    op.create_index('ix_training_specialists_department_factory', 'training_specialists', ['department', 'factory'], unique=True, schema='hr')


def downgrade() -> None:
    op.drop_index('ix_training_specialists_department_factory', table_name='training_specialists', schema='hr')
    op.drop_table('training_specialists', schema='hr')
    op.drop_index('ix_training_sessions_status', table_name='training_sessions', schema='hr')
    op.drop_index('ix_training_sessions_training_date', table_name='training_sessions', schema='hr')
    op.drop_index('ix_training_sessions_department', table_name='training_sessions', schema='hr')
    op.drop_table('training_sessions', schema='hr')
