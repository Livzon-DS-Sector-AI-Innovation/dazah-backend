"""merge_all_pending_heads

Revision ID: 77472813e846
Revises: 20260611_0001, 20260611_0004, b1a51f063719, f1a2b3c4d5e6
Create Date: 2026-06-12 02:28:28.186526
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '77472813e846'
down_revision: Union[str, None] = ('20260611_0001', '20260611_0004', 'b1a51f063719', 'f1a2b3c4d5e6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
