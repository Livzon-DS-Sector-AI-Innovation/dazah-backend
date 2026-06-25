"""xbj3 final merge all branches (recruitment + admin + training)

Merge the XBJ existing head (4cc3ba128fb9, recruitment + admin + regulations)
with the training-branch head (d279abb52bcf, product + material BOM + training
ledgers + annual plans + new-factory clone tables).

Revision ID: xbj3_final_001
Revises: 4cc3ba128fb9, d279abb52bcf
Create Date: 2026-06-15 17:00:00.000000

"""
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "xbj3_final_001"
down_revision: Union[str, Sequence[str], None] = ("4cc3ba128fb9", "d279abb52bcf")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """No-op merge revision."""
    pass


def downgrade() -> None:
    """No-op merge revision."""
    pass
