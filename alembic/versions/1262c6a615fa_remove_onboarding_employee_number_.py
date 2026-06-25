"""remove onboarding employee_number unique constraint

Revision ID: 1262c6a615fa
Revises: 5dca4c22ecc0
Create Date: 2026-06-08 10:40:40.754543
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1262c6a615fa'
down_revision: Union[str, None] = '5dca4c22ecc0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            """
            SELECT 1 FROM pg_constraint
            WHERE conname = 'onboarding_records_employee_number_key'
            AND conrelid = 'hr.onboarding_records'::regclass
            """
        )
    )
    if result.fetchone():
        op.drop_constraint(
            "onboarding_records_employee_number_key",
            "onboarding_records",
            schema="hr",
            type_="unique",
        )


def downgrade() -> None:
    op.create_unique_constraint(
        "onboarding_records_employee_number_key",
        "onboarding_records",
        ["employee_number"],
        schema="hr",
    )
