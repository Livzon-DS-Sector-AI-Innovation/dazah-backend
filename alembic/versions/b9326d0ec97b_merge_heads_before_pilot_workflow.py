"""merge heads before pilot workflow

Revision ID: b9326d0ec97b
Revises: 77472813e846, abdaf2f5b61f, f156d363a77f
Create Date: 2026-06-16 20:13:49.389009
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b9326d0ec97b'
down_revision: Union[str, None] = ('77472813e846', 'abdaf2f5b61f', 'f156d363a77f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
