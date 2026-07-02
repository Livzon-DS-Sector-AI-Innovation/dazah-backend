"""merge hplc_reference and audit_log_heads

Revision ID: f1ce4c737dbd
Revises: 20260629_0001, 9eb06fadeeb7
Create Date: 2026-06-29 12:08:04.704608
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1ce4c737dbd'
down_revision: Union[str, None] = ('20260629_0001', '9eb06fadeeb7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
