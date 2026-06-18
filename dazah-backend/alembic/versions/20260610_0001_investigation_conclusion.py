"""添加调查结论字段

Revision ID: investigation_conclusion_001
Revises: ai_config_001
Create Date: 2026-06-10 10:00:00

"""
from typing import Sequence, Any
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'investigation_conclusion_001'
down_revision: str = 'ai_config_001'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 为调查表添加调查结论字段
    op.add_column(
        'quality_deviation_investigations',
        sa.Column('investigation_conclusion', sa.Text(), nullable=True),
        schema='quality'
    )


def downgrade() -> None:
    op.drop_column(
        'quality_deviation_investigations',
        'investigation_conclusion',
        schema='quality'
    )