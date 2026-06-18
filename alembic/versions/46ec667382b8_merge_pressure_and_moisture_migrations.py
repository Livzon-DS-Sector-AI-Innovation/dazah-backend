"""merge_pressure_and_moisture_migrations

Revision ID: 46ec667382b8
Revises: 20260617_0001, c3d4e5f6g7h8
Create Date: 2026-06-18 11:18:50.056230
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '46ec667382b8'
down_revision: Union[str, None] = ('20260617_0001', 'c3d4e5f6g7h8')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
