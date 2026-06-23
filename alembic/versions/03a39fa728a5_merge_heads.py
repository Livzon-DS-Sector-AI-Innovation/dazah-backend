"""merge heads

Revision ID: 03a39fa728a5
Revises: 190bbff9dc50, cdfd8d9991b4
Create Date: 2026-06-20 00:30:02.477852
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '03a39fa728a5'
down_revision: Union[str, None] = ('190bbff9dc50', 'cdfd8d9991b4')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
