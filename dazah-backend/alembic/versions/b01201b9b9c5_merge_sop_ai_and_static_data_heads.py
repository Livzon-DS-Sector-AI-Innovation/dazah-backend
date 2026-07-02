"""merge sop_ai and static_data heads

Revision ID: b01201b9b9c5
Revises: 20260626_0002, 20260628_0001
Create Date: 2026-06-28 13:14:13.577289
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b01201b9b9c5'
down_revision: Union[str, None] = ('20260626_0002', '20260628_0001')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
