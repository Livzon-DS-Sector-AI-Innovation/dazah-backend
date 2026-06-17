"""add waiting_approval to pilot workflow

Revision ID: a1b2c3d4e5f6
Revises: 87a6ee7c69ca
Create Date: 2026-06-17 11:00:00.000000
"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '87a6ee7c69ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Update workflow status constraint
    op.drop_constraint('ck_pilot_workflows_status', 'pilot_workflows', schema='research')
    op.create_check_constraint(
        'ck_pilot_workflows_status',
        'pilot_workflows',
        "status IN ('pending', 'running', 'waiting_approval', 'completed', 'failed')",
        schema='research',
    )

    # Update step status constraint
    op.drop_constraint('ck_pilot_workflow_steps_status', 'pilot_workflow_steps', schema='research')
    op.create_check_constraint(
        'ck_pilot_workflow_steps_status',
        'pilot_workflow_steps',
        "status IN ('pending', 'running', 'waiting_approval', 'completed', 'failed', 'skipped')",
        schema='research',
    )


def downgrade() -> None:
    # Revert workflow status constraint
    op.drop_constraint('ck_pilot_workflows_status', 'pilot_workflows', schema='research')
    op.create_check_constraint(
        'ck_pilot_workflows_status',
        'pilot_workflows',
        "status IN ('pending', 'running', 'completed', 'failed')",
        schema='research',
    )

    # Revert step status constraint
    op.drop_constraint('ck_pilot_workflow_steps_status', 'pilot_workflow_steps', schema='research')
    op.create_check_constraint(
        'ck_pilot_workflow_steps_status',
        'pilot_workflow_steps',
        "status IN ('pending', 'running', 'completed', 'failed', 'skipped')",
        schema='research',
    )
