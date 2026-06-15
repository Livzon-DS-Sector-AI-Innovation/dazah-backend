"""add alert tables and update energy types

Revision ID: 1fa57660ca98
Revises: 62d4ceac12b4
Create Date: 2026-06-08 09:52:22.359516
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '1fa57660ca98'
down_revision: Union[str, None] = 'fd513f53016e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    
    # ── 1. 更新 CHECK 约束: steam → gas (only if old constraint exists) ──
    result = conn.execute(sa.text(
        "SELECT conname FROM pg_constraint "
        "WHERE conname = 'ck_energy_device_config_energy_type'"
    ))
    if result.fetchone():
        try:
            op.execute(
                "ALTER TABLE energy.energy_device_configs "
                "DROP CONSTRAINT ck_energy_device_config_energy_type"
            )
            op.execute(
                "ALTER TABLE energy.energy_device_configs "
                "ADD CONSTRAINT ck_energy_device_config_energy_type "
                "CHECK (energy_type IN ('electricity', 'water', 'gas'))"
            )
        except Exception:
            pass  # Constraint might already be updated

    # ── 2. energy_alert_rules (only if not exists) ──
    result = conn.execute(sa.text(
        "SELECT tablename FROM pg_tables "
        "WHERE schemaname = 'energy' AND tablename = 'energy_alert_rules'"
    ))
    if not result.fetchone():
        op.create_table(
            "energy_alert_rules",
            sa.Column("rule_name", sa.String(200), nullable=False),
            sa.Column("rule_description", sa.Text(), nullable=True),
            sa.Column("energy_type", sa.String(20), nullable=False),
            sa.Column("monitor_metric", sa.String(20), nullable=False),
            sa.Column("threshold_type", sa.String(20), nullable=False),
            sa.Column("threshold_value", sa.Numeric(18, 4), nullable=False),
            sa.Column("unit", sa.String(20), nullable=False),
            sa.Column("alert_level", sa.String(20), nullable=False),
            sa.Column("notify_method", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
            sa.Column("notify_users", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
            sa.Column("notify_frequency", sa.String(20), nullable=False),
            sa.Column("effective_time", sa.String(20), nullable=False),
            sa.Column("custom_time_start", sa.String(8), nullable=True),
            sa.Column("custom_time_end", sa.String(8), nullable=True),
            sa.Column("is_enabled", sa.Boolean(), nullable=False),
            sa.Column("id", sa.Uuid(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("created_by", sa.Uuid(), nullable=True),
            sa.Column("updated_by", sa.Uuid(), nullable=True),
            sa.Column("is_deleted", sa.Boolean(), server_default="false", nullable=False),
            sa.ForeignKeyConstraint(["created_by"], ["identity.users.id"]),
            sa.ForeignKeyConstraint(["updated_by"], ["identity.users.id"]),
            sa.PrimaryKeyConstraint("id"),
            schema="energy",
        )

    # ── 3. energy_alert_records (only if not exists) ──
    result = conn.execute(sa.text(
        "SELECT tablename FROM pg_tables "
        "WHERE schemaname = 'energy' AND tablename = 'energy_alert_records'"
    ))
    if not result.fetchone():
        op.create_table(
            "energy_alert_records",
            sa.Column("rule_id", sa.Uuid(), nullable=False),
            sa.Column("device_config_id", sa.Uuid(), nullable=True),
            sa.Column("energy_type", sa.String(20), nullable=False),
            sa.Column("alert_level", sa.String(20), nullable=False),
            sa.Column("trigger_value", sa.Numeric(18, 4), nullable=False),
            sa.Column("threshold_value", sa.Numeric(18, 4), nullable=False),
            sa.Column("unit", sa.String(20), nullable=False),
            sa.Column("alert_time", sa.DateTime(timezone=True), nullable=False),
            sa.Column("status", sa.String(20), nullable=False),
            sa.Column("processed_by", sa.String(100), nullable=True),
            sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("process_note", sa.Text(), nullable=True),
            sa.Column("id", sa.Uuid(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("created_by", sa.Uuid(), nullable=True),
            sa.Column("updated_by", sa.Uuid(), nullable=True),
            sa.Column("is_deleted", sa.Boolean(), server_default="false", nullable=False),
            sa.ForeignKeyConstraint(["created_by"], ["identity.users.id"]),
            sa.ForeignKeyConstraint(["updated_by"], ["identity.users.id"]),
            sa.ForeignKeyConstraint(["rule_id"], ["energy.energy_alert_rules.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            schema="energy",
        )


def downgrade() -> None:
    op.drop_table("energy_alert_records", schema="energy")
    op.drop_table("energy_alert_rules", schema="energy")
