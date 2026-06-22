"""add ai analysis to regulatory docs

Revision ID: d4e8f2a9b3c5
Revises: c3d7f9e2a1b8
Create Date: 2026-06-22 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = 'd4e8f2a9b3c5'
down_revision: Union[str, None] = 'c3d7f9e2a1b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('regulatory_documents', 
        sa.Column('ai_summary', sa.Text(), nullable=True, comment='AI 生成的文档摘要'),
        schema='regulatory_tracker'
    )
    op.add_column('regulatory_documents',
        sa.Column('ai_key_points', JSONB(), nullable=True, comment='AI 提取的关键要点'),
        schema='regulatory_tracker'
    )
    op.add_column('regulatory_documents',
        sa.Column('ai_relevance_score', sa.Float(), nullable=True, comment='AI 评估的相关性评分 (0-1)'),
        schema='regulatory_tracker'
    )
    op.add_column('regulatory_documents',
        sa.Column('ai_analyzed_at', sa.DateTime(timezone=True), nullable=True, comment='AI 分析完成时间'),
        schema='regulatory_tracker'
    )
    op.add_column('regulatory_documents',
        sa.Column('ai_analysis_status', sa.String(50), nullable=True, comment='AI 分析状态: pending/completed/failed'),
        schema='regulatory_tracker'
    )


def downgrade() -> None:
    op.drop_column('regulatory_documents', 'ai_analysis_status', schema='regulatory_tracker')
    op.drop_column('regulatory_documents', 'ai_analyzed_at', schema='regulatory_tracker')
    op.drop_column('regulatory_documents', 'ai_relevance_score', schema='regulatory_tracker')
    op.drop_column('regulatory_documents', 'ai_key_points', schema='regulatory_tracker')
    op.drop_column('regulatory_documents', 'ai_summary', schema='regulatory_tracker')
