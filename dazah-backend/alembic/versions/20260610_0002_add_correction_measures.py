"""添加整改措施字段（correction_measures）

Revision ID: 20260610_0002
Revises: investigation_conclusion_001
Create Date: 2026-06-10 11:30:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID


# revision identifiers, used by Alembic.
revision = '20260610_0002'
down_revision = 'investigation_conclusion_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 添加 correction_measures 字段到整改表
    op.add_column(
        'quality_deviation_corrections',
        sa.Column('correction_measures', sa.Text(), nullable=True, comment='整改措施（CA+PA）'),
        schema='quality'
    )


def downgrade() -> None:
    op.drop_column(
        'quality_deviation_corrections',
        'correction_measures',
        schema='quality'
    )