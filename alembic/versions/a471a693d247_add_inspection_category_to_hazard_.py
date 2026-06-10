"""add inspection_category to hazard_reports

Revision ID: a471a693d247
Revises: d0b8bf6149e6
Create Date: 2026-06-09 17:44:48.372086
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a471a693d247'
down_revision: Union[str, None] = 'd0b8bf6149e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'hazard_reports',
        sa.Column(
            'inspection_category',
            sa.String(length=64),
            nullable=True,
            comment='检查类别（日常检查/专项检查…）',
        ),
        schema='safety',
    )


def downgrade() -> None:
    op.drop_column('hazard_reports', 'inspection_category', schema='safety')
