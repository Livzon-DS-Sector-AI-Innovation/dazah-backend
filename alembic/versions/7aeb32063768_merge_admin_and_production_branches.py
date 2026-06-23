"""merge admin and production branches

Revision ID: 7aeb32063768
Revises: 65acf67e248f, b340473e09ef
Create Date: 2026-06-08 14:54:04.456801
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7aeb32063768'
down_revision: Union[str, None] = ('65acf67e248f', 'b340473e09ef')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
