"""merge_all_heads

Revision ID: d3e356a620f0
Revises: 77472813e846, f156d363a77f, abdaf2f5b61f
Create Date: 2026-06-16 17:09:58.617275
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3e356a620f0'
down_revision: Union[str, None] = ('77472813e846', 'f156d363a77f', 'abdaf2f5b61f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
