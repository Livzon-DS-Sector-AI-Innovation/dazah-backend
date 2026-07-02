"""merge audit log head into main

Revision ID: 9eb06fadeeb7
Revises: b01201b9b9c5, 20250629_0001
Create Date: 2026-06-29 09:00:56.570195
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9eb06fadeeb7'
down_revision: Union[str, None] = ('b01201b9b9c5', '20250629_0001')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
