"""merge hazard_revision_drop and departments branches

Revision ID: 2a3acacefbdf
Revises: 62d4ceac12b4, 824fbcebd3f2
Create Date: 2026-06-08 17:51:05.125293
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a3acacefbdf'
down_revision: Union[str, None] = ('62d4ceac12b4', '824fbcebd3f2')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
