"""merge all heads

Revision ID: 4cc3ba128fb9
Revises: 494e3004c6fe, f3a9e2b1c8d4, f433f7bcd8f9
Create Date: 2026-06-15 09:14:01.462272
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4cc3ba128fb9'
down_revision: Union[str, None] = ('494e3004c6fe', 'f3a9e2b1c8d4', 'f433f7bcd8f9')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
