"""add reference_substances table

Revision ID: a1b2c3d4e5f6
Revises: d3e356a620f0
Create Date: 2026-06-16 21:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'd3e356a620f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'reference_substances',
        sa.Column('drug_name', sa.String(255), nullable=False, comment='药品名称'),
        sa.Column('substance_name', sa.String(255), nullable=False, comment='对照物质名称'),
        sa.Column('lot_number', sa.String(100), nullable=False, comment='批号'),
        sa.Column('manufacturer', sa.String(500), nullable=False, comment='生产厂家/来源'),
        sa.Column('english_name', sa.String(255), nullable=True, comment='英文名'),
        sa.Column('expiration_date', sa.String(50), nullable=True, comment='有效期'),
        sa.Column('cas_number', sa.String(50), nullable=True, comment='CAS号'),
        sa.Column('molecular_formula', sa.String(100), nullable=True, comment='分子式'),
        sa.Column('molecular_weight', sa.String(50), nullable=True, comment='分子量'),
        sa.Column('assay', sa.String(50), nullable=True, comment='含量'),
        sa.Column('storage_condition', sa.String(255), nullable=True, comment='贮存条件'),
        sa.Column('usage_scope', sa.String(255), nullable=True, server_default='含量测定', comment='使用范围'),
        sa.Column('usage_method', sa.String(255), nullable=True, server_default='直接折算', comment='使用方法'),
        sa.Column('coa_file_url', sa.Text, nullable=True, comment='COA文件URL'),
        sa.Column('provider', sa.String(255), nullable=False, server_default='珠海保税区丽珠合成制药有限公司', comment='提供单位'),
        sa.Column('handler', sa.String(50), nullable=False, server_default='魏永红', comment='经办人'),
        sa.Column('contact', sa.String(50), nullable=False, server_default='13570680132', comment='联系方式'),
        sa.Column('id', sa.Uuid(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_by', sa.Uuid(as_uuid=True), nullable=True),
        sa.Column('updated_by', sa.Uuid(as_uuid=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.PrimaryKeyConstraint('id'),
        schema='registration',
    )


def downgrade() -> None:
    op.drop_table('reference_substances', schema='registration')
