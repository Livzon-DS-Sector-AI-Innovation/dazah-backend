"""add_prejob_training_plan_templates

Revision ID: 04b755952fcf
Revises: 03a754851ebe
Create Date: 2026-06-30 17:30:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '04b755952fcf'
down_revision: Union[str, None] = '03a754851ebe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "prejob_training_plan_templates",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("department", sa.String(64), nullable=False, comment="部门名称"),
        sa.Column("factory", sa.String(8), nullable=False, server_default="old", comment="厂区: old=旧厂, new=新厂"),
        sa.Column("items", postgresql.JSON(), nullable=False, server_default="[]", comment="培训计划条目列表 [{seq, content, deadline, trainer}]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("department", "factory", name="ix_prejob_template_dept_factory"),
        schema="hr",
    )


def downgrade() -> None:
    op.drop_table("prejob_training_plan_templates", schema="hr")
