"""add material_bom table to production schema

Revision ID: b340473e09ef
Revises: 1262c6a615fa
Create Date: 2026-06-08 14:20:01.371451
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b340473e09ef'
down_revision: Union[str, None] = '1262c6a615fa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'material_boms',
        sa.Column('name', sa.String(length=128), nullable=False, comment='物料名称'),
        sa.Column('code', sa.String(length=64), nullable=True, comment='物料代号'),
        sa.Column('manufacturer', sa.String(length=128), nullable=True, comment='生产商'),
        sa.Column('material_level', sa.String(length=64), nullable=True, comment='物料级别'),
        sa.Column('document_name', sa.String(length=256), nullable=True, comment='文件名称'),
        sa.Column('quality_standard', sa.String(length=256), nullable=True, comment='质量标准'),
        sa.Column('process_name', sa.String(length=128), nullable=True, comment='工艺名称'),
        sa.Column('feishu_record_id', sa.String(length=32), nullable=True, comment='飞书多维表格 record_id'),
        sa.Column('feishu_synced_at', sa.Date(), nullable=True, comment='上次飞书同步时间'),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['identity.users.id']),
        sa.ForeignKeyConstraint(['updated_by'], ['identity.users.id']),
        sa.PrimaryKeyConstraint('id'),
        schema='production'
    )
    op.create_index('ix_material_boms_name', 'material_boms', ['name'], unique=False, schema='production')
    op.create_index('ix_material_boms_code', 'material_boms', ['code'], unique=False, schema='production')
    op.create_index('ix_material_boms_feishu_record_id', 'material_boms', ['feishu_record_id'], unique=False, schema='production')


def downgrade() -> None:
    op.drop_index('ix_material_boms_feishu_record_id', table_name='material_boms', schema='production')
    op.drop_index('ix_material_boms_code', table_name='material_boms', schema='production')
    op.drop_index('ix_material_boms_name', table_name='material_boms', schema='production')
    op.drop_table('material_boms', schema='production')
