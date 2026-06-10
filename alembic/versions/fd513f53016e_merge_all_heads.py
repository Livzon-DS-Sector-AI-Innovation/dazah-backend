"""merge_all_heads

Revision ID: fd513f53016e
Revises: 20260610_0002, 20260611_0002, 983fbcb39a01
Create Date: 2026-06-10 11:01:27.534063
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fd513f53016e'
down_revision: Union[str, None] = ('20260610_0002', '20260611_0002', '983fbcb39a01')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
