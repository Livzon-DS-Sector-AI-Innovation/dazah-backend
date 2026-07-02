"""add_training_teams_table

Revision ID: 03a754851ebe
Revises: ba19731e097a
Create Date: 2026-06-30 16:06:56.012144
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '03a754851ebe'
down_revision: Union[str, None] = 'ba19731e097a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "training_teams",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(128), nullable=False, comment="班组名称"),
        sa.Column("factory", sa.String(8), nullable=False, server_default="old", comment="厂区: old=旧厂, new=新厂"),
        sa.Column("department", sa.String(64), nullable=False, comment="所属部门"),
        sa.Column("specialist_employee_number", sa.String(32), nullable=False, comment="培训专员工号"),
        sa.Column("specialist_name", sa.String(64), nullable=False, comment="培训专员姓名"),
        sa.Column("employee_names", postgresql.JSON(), nullable=True, comment="受训人员姓名列表"),
        sa.Column("employee_numbers", postgresql.JSON(), nullable=True, comment="受训人员工号列表"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_by", sa.String(64), nullable=True),
        sa.Column("updated_by", sa.String(64), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.PrimaryKeyConstraint("id"),
        schema="hr",
    )


def downgrade() -> None:
    op.drop_table("training_teams", schema="hr")
