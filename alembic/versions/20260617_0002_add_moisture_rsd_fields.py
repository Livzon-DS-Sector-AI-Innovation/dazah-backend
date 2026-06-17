"""add moisture and rsd fields to reference_standards

Revision ID: c3d4e5f6g7h8
Revises: b2c3d4e5f6g7
Create Date: 2026-06-17 14:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3d4e5f6g7h8'
down_revision = 'b2c3d4e5f6g7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 添加 moisture 字段
    op.add_column(
        'reference_standards',
        sa.Column('moisture', sa.String(length=64), nullable=True, comment='水分/干燥失重'),
        schema='registration'
    )
    
    # 添加 rsd 字段
    op.add_column(
        'reference_standards',
        sa.Column('rsd', sa.String(length=64), nullable=True, comment='RSD'),
        schema='registration'
    )


def downgrade() -> None:
    # 删除 rsd 字段
    op.drop_column('reference_standards', 'rsd', schema='registration')
    
    # 删除 moisture 字段
    op.drop_column('reference_standards', 'moisture', schema='registration')
