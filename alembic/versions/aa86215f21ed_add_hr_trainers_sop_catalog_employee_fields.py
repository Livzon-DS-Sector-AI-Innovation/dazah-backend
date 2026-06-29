"""add hr trainers, sop_catalog, employee concurrent_departments & sort_order

Revision ID: aa86215f21ed
Revises: 284c3b08d3dc
Create Date: 2026-06-29 16:30:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aa86215f21ed'
down_revision: Union[str, None] = '284c3b08d3dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── hr.employees: add concurrent_departments ──
    op.add_column(
        'employees',
        sa.Column('concurrent_departments', sa.String(256), nullable=True, comment='兼任部门'),
        schema='hr',
    )
    # ── hr.employees: add sort_order ──
    op.add_column(
        'employees',
        sa.Column('sort_order', sa.Integer(), nullable=True, comment='Excel行序号'),
        schema='hr',
    )

    # ── hr.trainers ──
    op.create_table(
        'trainers',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('name', sa.String(64), nullable=False),
        sa.Column('department', sa.String(64), nullable=True),
        sa.Column('trainable_departments', sa.Text(), nullable=True, comment='可培训部门'),
        sa.Column('qualification_scope', sa.Text(), nullable=True, comment='资格范围'),
        sa.Column('certification_date', sa.Date(), nullable=True),
        sa.Column('confirmation_date', sa.Date(), nullable=True),
        sa.Column('confirmation_reminder', sa.Date(), nullable=True),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('is_primary_trainer', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('admin', sa.String(64), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='hr',
    )
    op.create_index('ix_trainers_department', 'trainers', ['department'], schema='hr')
    op.create_index('ix_trainers_name', 'trainers', ['name'], schema='hr')

    # ── hr.sop_catalog ──
    op.create_table(
        'sop_catalog',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('file_name', sa.String(256), nullable=False),
        sa.Column('sop_number', sa.String(64), nullable=True),
        sa.Column('category', sa.String(128), nullable=True),
        sa.Column('department', sa.String(128), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='hr',
    )
    op.create_index('ix_sop_catalog_department', 'sop_catalog', ['department'], schema='hr')
    op.create_index('ix_sop_catalog_category', 'sop_catalog', ['category'], schema='hr')


def downgrade() -> None:
    # ── hr.sop_catalog ──
    op.drop_index('ix_sop_catalog_category', table_name='sop_catalog', schema='hr')
    op.drop_index('ix_sop_catalog_department', table_name='sop_catalog', schema='hr')
    op.drop_table('sop_catalog', schema='hr')

    # ── hr.trainers ──
    op.drop_index('ix_trainers_name', table_name='trainers', schema='hr')
    op.drop_index('ix_trainers_department', table_name='trainers', schema='hr')
    op.drop_table('trainers', schema='hr')

    # ── hr.employees: drop sort_order ──
    op.drop_column('employees', 'sort_order', schema='hr')
    # ── hr.employees: drop concurrent_departments ──
    op.drop_column('employees', 'concurrent_departments', schema='hr')
