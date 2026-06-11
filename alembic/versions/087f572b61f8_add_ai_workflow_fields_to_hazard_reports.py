"""add ai workflow fields to hazard_reports

Revision ID: 087f572b61f8
Revises: 2a3acacefbdf
Create Date: 2026-06-08 17:52:31.599708
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '087f572b61f8'
down_revision: Union[str, None] = '2a3acacefbdf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'hazard_reports',
        sa.Column(
            'ai_node_progress',
            sa.String(length=50),
            server_default='pending_input',
            nullable=False,
            comment='AI流程节点进度(pending_input/pending_script1/review_script1/pending_script2/review_script2/completed)',
        ),
        schema='safety',
    )
    op.add_column(
        'hazard_reports',
        sa.Column(
            'overall_status',
            sa.String(length=20),
            server_default='draft',
            nullable=False,
            comment='整体状态(draft/ai_processing/completed/cancelled)',
        ),
        schema='safety',
    )
    op.add_column(
        'hazard_reports',
        sa.Column(
            'ai_error_message',
            sa.Text(),
            nullable=True,
            comment='AI 脚本执行错误信息',
        ),
        schema='safety',
    )
    op.add_column(
        'hazard_reports',
        sa.Column(
            'script1_review_status',
            sa.String(length=20),
            server_default='pending',
            nullable=False,
            comment='AI隐患识别审核状态(pending/approved/rejected)',
        ),
        schema='safety',
    )
    op.add_column(
        'hazard_reports',
        sa.Column(
            'script2_review_status',
            sa.String(length=20),
            server_default='pending',
            nullable=False,
            comment='AI整改建议审核状态(pending/approved/rejected)',
        ),
        schema='safety',
    )
    op.add_column(
        'hazard_reports',
        sa.Column(
            'ai_generated',
            sa.Boolean(),
            server_default='false',
            nullable=False,
            comment='是否AI生成',
        ),
        schema='safety',
    )


def downgrade() -> None:
    op.drop_column('hazard_reports', 'ai_generated', schema='safety')
    op.drop_column('hazard_reports', 'script2_review_status', schema='safety')
    op.drop_column('hazard_reports', 'script1_review_status', schema='safety')
    op.drop_column('hazard_reports', 'ai_error_message', schema='safety')
    op.drop_column('hazard_reports', 'overall_status', schema='safety')
    op.drop_column('hazard_reports', 'ai_node_progress', schema='safety')
