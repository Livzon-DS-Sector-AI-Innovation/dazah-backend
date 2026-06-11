"""fix dossier_writer missing base model columns

Revision ID: 20260611_0004
Revises: 20260611_0003
Create Date: 2026-06-11 13:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by the revision.
revision = '20260611_0004'
down_revision = '20260611_0003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add missing BaseModel columns to dossier_templates
    op.add_column('dossier_templates', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False), schema='dossier_writer')
    op.add_column('dossier_templates', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False), schema='dossier_writer')
    op.add_column('dossier_templates', sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True), schema='dossier_writer')
    op.add_column('dossier_templates', sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True), schema='dossier_writer')
    op.add_column('dossier_templates', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'), schema='dossier_writer')

    # Add missing BaseModel columns to chapter_assets
    op.add_column('chapter_assets', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False), schema='dossier_writer')
    op.add_column('chapter_assets', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False), schema='dossier_writer')
    op.add_column('chapter_assets', sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True), schema='dossier_writer')
    op.add_column('chapter_assets', sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True), schema='dossier_writer')
    op.add_column('chapter_assets', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'), schema='dossier_writer')


def downgrade() -> None:
    # Remove columns from chapter_assets
    op.drop_column('chapter_assets', 'is_deleted', schema='dossier_writer')
    op.drop_column('chapter_assets', 'updated_by', schema='dossier_writer')
    op.drop_column('chapter_assets', 'created_by', schema='dossier_writer')
    op.drop_column('chapter_assets', 'updated_at', schema='dossier_writer')
    op.drop_column('chapter_assets', 'created_at', schema='dossier_writer')

    # Remove columns from dossier_templates
    op.drop_column('dossier_templates', 'is_deleted', schema='dossier_writer')
    op.drop_column('dossier_templates', 'updated_by', schema='dossier_writer')
    op.drop_column('dossier_templates', 'created_by', schema='dossier_writer')
    op.drop_column('dossier_templates', 'updated_at', schema='dossier_writer')
    op.drop_column('dossier_templates', 'created_at', schema='dossier_writer')
