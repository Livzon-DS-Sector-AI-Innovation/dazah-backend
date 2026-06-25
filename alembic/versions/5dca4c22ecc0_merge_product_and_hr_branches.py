"""merge product and hr branches

Revision ID: 5dca4c22ecc0
Revises: 1708e4a95e16, 2eba70488232
Create Date: 2026-06-08 10:32:51.504215
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5dca4c22ecc0'
down_revision: Union[str, None] = ('1708e4a95e16', '2eba70488232')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
