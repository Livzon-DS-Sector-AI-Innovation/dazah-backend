"""add reference_standards table

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-17 12:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'b2c3d4e5f6g7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'reference_standards',
        sa.Column('drug_name', sa.String(128), nullable=False, comment='药品名称'),
        sa.Column('reference_substance_name', sa.String(256), nullable=True, comment='对照物质名称'),
        sa.Column('batch_number', sa.String(64), nullable=True, comment='批号'),
        sa.Column('manufacturer', sa.String(256), nullable=True, comment='生产厂家/来源'),
        sa.Column('english_name', sa.String(256), nullable=True, comment='英文名'),
        sa.Column('molecular_formula', sa.String(128), nullable=True, comment='分子式'),
        sa.Column('molecular_weight', sa.String(64), nullable=True, comment='分子量'),
        sa.Column('cas_number', sa.String(64), nullable=True, comment='CAS号'),
        sa.Column('content', sa.String(64), nullable=True, comment='含量'),
        sa.Column('expiration_date', sa.String(64), nullable=True, comment='有效期'),
        sa.Column('storage_condition', sa.String(128), nullable=True, comment='贮存条件'),
        sa.Column('coa_file_key', sa.String(256), nullable=False, comment='COA文件 key'),
        sa.Column('coa_file_name', sa.String(256), nullable=True, comment='COA文件名'),
        sa.Column('output_file_key', sa.String(256), nullable=False, comment='生成文件 key'),
        sa.Column('output_file_name', sa.String(256), nullable=False, comment='生成文件名'),
        sa.Column('remarks', sa.Text, nullable=True, comment='备注'),
        sa.Column('id', sa.Uuid(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_by', sa.Uuid(as_uuid=True), nullable=True),
        sa.Column('updated_by', sa.Uuid(as_uuid=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.PrimaryKeyConstraint('id'),
        schema='registration',
    )
    op.create_index('ix_reference_standards_drug_name', 'reference_standards', ['drug_name'], schema='registration')
    op.create_index('ix_reference_standards_batch_number', 'reference_standards', ['batch_number'], schema='registration')


def downgrade() -> None:
    op.drop_index('ix_reference_standards_batch_number', table_name='reference_standards', schema='registration')
    op.drop_index('ix_reference_standards_drug_name', table_name='reference_standards', schema='registration')
    op.drop_table('reference_standards', schema='registration')
