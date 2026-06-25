"""add core llm configs

Revision ID: c3d7f9e2a1b8
Revises: b8f3e9a2c1d7
Create Date: 2026-06-18 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d7f9e2a1b8'
down_revision: Union[str, None] = 'b8f3e9a2c1d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create core schema
    op.execute("CREATE SCHEMA IF NOT EXISTS core")
    
    # Create llm_configs table
    op.create_table(
        'llm_configs',
        sa.Column('id', sa.Uuid(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_by', sa.Uuid(as_uuid=True), nullable=True),
        sa.Column('updated_by', sa.Uuid(as_uuid=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('config_name', sa.String(128), nullable=False, comment='Configuration name'),
        sa.Column('config_type', sa.String(20), server_default='text', nullable=False, comment='Config type: text / vision'),
        sa.Column('api_base_url', sa.String(500), nullable=False, comment='API base URL'),
        sa.Column('encrypted_api_key', sa.String(1000), nullable=False, comment='Encrypted API key'),
        sa.Column('model_name', sa.String(128), nullable=False, comment='Model name'),
        sa.Column('temperature', sa.Float(), server_default='0.1', nullable=False, comment='Temperature'),
        sa.Column('timeout_seconds', sa.Integer(), server_default='120', nullable=False, comment='Timeout seconds'),
        sa.Column('is_active', sa.Boolean(), server_default='false', nullable=False, comment='Is active config'),
        sa.Column('notes', sa.Text(), nullable=True, comment='Notes'),
        sa.ForeignKeyConstraint(['created_by'], ['identity.users.id']),
        sa.ForeignKeyConstraint(['updated_by'], ['identity.users.id']),
        sa.PrimaryKeyConstraint('id'),
        schema='core',
        comment='LLM configuration table'
    )


def downgrade() -> None:
    op.drop_table('llm_configs', schema='core')
