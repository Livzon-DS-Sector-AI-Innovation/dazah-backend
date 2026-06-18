"""quality inspection standards tables

Revision ID: 20260602_0002
Revises: 20260602_0001
Create Date: 2026-06-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260602_0002"
down_revision: str | None = "20260602_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ========== Inspection Standards (Quality Standards Master) ==========
    op.create_table(
        "inspection_standards",
        sa.Column("standard_no", sa.String(length=64), nullable=False),
        sa.Column("material_code", sa.String(length=64), nullable=False),
        sa.Column("material_name", sa.String(length=255), nullable=True),
        sa.Column("cas_no", sa.String(length=32), nullable=True),
        sa.Column("material_category", sa.String(length=32), nullable=False),
        sa.Column("pharmacopeia", sa.String(length=32), nullable=True),
        sa.Column("version", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=32), server_default=sa.text("'draft'"), nullable=False),
        sa.Column("effective_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("obsolete_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_obsolete", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("obsolete_reason", sa.Text(), nullable=True),
        sa.Column("sop_no", sa.String(length=64), nullable=True),
        sa.Column("attachment_urls", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("source_version", sa.String(length=20), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["created_by"], ["identity.users.id"]),
        sa.ForeignKeyConstraint(["updated_by"], ["identity.users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("material_code", "version", name="uq_standards_material_version"),
        schema="quality",
    )
    op.create_index(
        "idx_standards_material_code", "inspection_standards", ["material_code"], unique=False, schema="quality"
    )
    op.create_index(
        "idx_standards_status", "inspection_standards", ["status"], unique=False, schema="quality"
    )
    op.create_index(
        "idx_standards_material_category", "inspection_standards", ["material_category"], unique=False, schema="quality"
    )
    op.create_index(
        "idx_standards_effective_date", "inspection_standards", ["effective_date"], unique=False, schema="quality"
    )

    # ========== Inspection Standard Items (Test Items) ==========
    op.create_table(
        "inspection_standard_items",
        sa.Column("standard_id", sa.Uuid(), nullable=False),
        sa.Column("item_no", sa.Integer(), nullable=False),
        sa.Column("item_name", sa.String(length=255), nullable=False),
        sa.Column("test_method", sa.Text(), nullable=True),
        sa.Column("instrument_code", sa.String(length=64), nullable=True),
        sa.Column("reference_materials", sa.String(length=500), nullable=True),
        sa.Column("limit_type", sa.String(length=32), nullable=False),
        sa.Column("合格限值", sa.String(length=255), nullable=True),
        sa.Column("item_category", sa.String(length=32), nullable=True),
        sa.Column("is_critical", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["standard_id"], ["quality.inspection_standards.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["identity.users.id"]),
        sa.ForeignKeyConstraint(["updated_by"], ["identity.users.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="quality",
    )
    op.create_index(
        "idx_standard_items_standard_id", "inspection_standard_items", ["standard_id"], unique=False, schema="quality"
    )

    # ========== Approval Records ==========
    op.create_table(
        "standard_approval_records",
        sa.Column("standard_id", sa.Uuid(), nullable=False),
        sa.Column("approval_level", sa.Integer(), nullable=False),
        sa.Column("approval_status", sa.String(length=32), nullable=False),
        sa.Column("approver_role", sa.String(length=64), nullable=True),
        sa.Column("approver_id", sa.Uuid(), nullable=True),
        sa.Column("approver_name", sa.String(length=100), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("comments", sa.Text(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["standard_id"], ["quality.inspection_standards.id"]),
        sa.ForeignKeyConstraint(["approver_id"], ["identity.users.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["identity.users.id"]),
        sa.ForeignKeyConstraint(["updated_by"], ["identity.users.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="quality",
    )
    op.create_index(
        "idx_approval_records_standard_id", "standard_approval_records", ["standard_id"], unique=False, schema="quality"
    )


def downgrade() -> None:
    op.drop_table("standard_approval_records", schema="quality")
    op.drop_table("inspection_standard_items", schema="quality")
    op.drop_table("inspection_standards", schema="quality")