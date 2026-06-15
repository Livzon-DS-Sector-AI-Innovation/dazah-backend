"""merge 20260611 and 20260612

Revision ID: f156d363a77f
Revises: 20260611_0001, 20260612_0001
Create Date: 2026-06-12 11:30:18.268331
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f156d363a77f'
down_revision: Union[str, None] = ('20260611_0001', '20260612_0001')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
