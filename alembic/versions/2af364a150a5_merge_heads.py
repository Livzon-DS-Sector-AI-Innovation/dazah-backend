"""merge heads

Revision ID: 2af364a150a5
Revises: f103dadd0ecd
Create Date: 2026-06-29 09:08:42.159308
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2af364a150a5'
down_revision: Union[str, None] = 'f103dadd0ecd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
