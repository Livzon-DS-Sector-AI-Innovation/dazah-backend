"""add_hazard_rectification_reply_and_three_level_verify

Revision ID: c70602651fd7
Revises: a471a693d247
Create Date: 2026-06-10 16:41:38.550529
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c70602651fd7'
down_revision: Union[str, None] = 'a471a693d247'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 整改回复字段
    op.add_column('hazard_reports', sa.Column('rectification_reply', sa.Text(), nullable=True, comment='整改回复内容'), schema='safety')
    op.add_column('hazard_reports', sa.Column('rectification_replied_at', sa.DateTime(timezone=True), nullable=True, comment='整改回复时间'), schema='safety')
    op.add_column('hazard_reports', sa.Column('rectification_replied_by', sa.UUID(), nullable=True, comment='整改回复人ID'), schema='safety')
    op.add_column('hazard_reports', sa.Column('rectification_replied_by_name', sa.String(length=100), nullable=True, comment='整改回复人姓名'), schema='safety')

    # 一级复核字段
    op.add_column('hazard_reports', sa.Column('verify_level_1_status', sa.String(length=20), server_default='pending', nullable=False, comment='一级复核状态: pending/approved/rejected'), schema='safety')
    op.add_column('hazard_reports', sa.Column('verify_level_1_by', sa.UUID(), nullable=True, comment='一级复核人ID'), schema='safety')
    op.add_column('hazard_reports', sa.Column('verify_level_1_by_name', sa.String(length=100), nullable=True, comment='一级复核人姓名'), schema='safety')
    op.add_column('hazard_reports', sa.Column('verify_level_1_at', sa.DateTime(timezone=True), nullable=True, comment='一级复核时间'), schema='safety')
    op.add_column('hazard_reports', sa.Column('verify_level_1_opinion', sa.Text(), nullable=True, comment='一级复核意见'), schema='safety')

    # 二级复核字段
    op.add_column('hazard_reports', sa.Column('verify_level_2_status', sa.String(length=20), server_default='pending', nullable=False, comment='二级复核状态: pending/approved/rejected'), schema='safety')
    op.add_column('hazard_reports', sa.Column('verify_level_2_by', sa.UUID(), nullable=True, comment='二级复核人ID'), schema='safety')
    op.add_column('hazard_reports', sa.Column('verify_level_2_by_name', sa.String(length=100), nullable=True, comment='二级复核人姓名'), schema='safety')
    op.add_column('hazard_reports', sa.Column('verify_level_2_at', sa.DateTime(timezone=True), nullable=True, comment='二级复核时间'), schema='safety')
    op.add_column('hazard_reports', sa.Column('verify_level_2_opinion', sa.Text(), nullable=True, comment='二级复核意见'), schema='safety')

    # 三级复核字段
    op.add_column('hazard_reports', sa.Column('verify_level_3_status', sa.String(length=20), server_default='pending', nullable=False, comment='三级复核状态: pending/approved/rejected'), schema='safety')
    op.add_column('hazard_reports', sa.Column('verify_level_3_by', sa.UUID(), nullable=True, comment='三级复核人ID'), schema='safety')
    op.add_column('hazard_reports', sa.Column('verify_level_3_by_name', sa.String(length=100), nullable=True, comment='三级复核人姓名'), schema='safety')
    op.add_column('hazard_reports', sa.Column('verify_level_3_at', sa.DateTime(timezone=True), nullable=True, comment='三级复核时间'), schema='safety')
    op.add_column('hazard_reports', sa.Column('verify_level_3_opinion', sa.Text(), nullable=True, comment='三级复核意见'), schema='safety')

    # 外键约束
    op.create_foreign_key(None, 'hazard_reports', 'users', ['rectification_replied_by'], ['id'], source_schema='safety', referent_schema='identity')
    op.create_foreign_key(None, 'hazard_reports', 'users', ['verify_level_1_by'], ['id'], source_schema='safety', referent_schema='identity')
    op.create_foreign_key(None, 'hazard_reports', 'users', ['verify_level_2_by'], ['id'], source_schema='safety', referent_schema='identity')
    op.create_foreign_key(None, 'hazard_reports', 'users', ['verify_level_3_by'], ['id'], source_schema='safety', referent_schema='identity')


def downgrade() -> None:
    # 外键约束
    op.drop_constraint(None, 'hazard_reports', schema='safety', type_='foreignkey')
    op.drop_constraint(None, 'hazard_reports', schema='safety', type_='foreignkey')
    op.drop_constraint(None, 'hazard_reports', schema='safety', type_='foreignkey')
    op.drop_constraint(None, 'hazard_reports', schema='safety', type_='foreignkey')

    # 三级复核字段
    op.drop_column('hazard_reports', 'verify_level_3_opinion', schema='safety')
    op.drop_column('hazard_reports', 'verify_level_3_at', schema='safety')
    op.drop_column('hazard_reports', 'verify_level_3_by_name', schema='safety')
    op.drop_column('hazard_reports', 'verify_level_3_by', schema='safety')
    op.drop_column('hazard_reports', 'verify_level_3_status', schema='safety')

    # 二级复核字段
    op.drop_column('hazard_reports', 'verify_level_2_opinion', schema='safety')
    op.drop_column('hazard_reports', 'verify_level_2_at', schema='safety')
    op.drop_column('hazard_reports', 'verify_level_2_by_name', schema='safety')
    op.drop_column('hazard_reports', 'verify_level_2_by', schema='safety')
    op.drop_column('hazard_reports', 'verify_level_2_status', schema='safety')

    # 一级复核字段
    op.drop_column('hazard_reports', 'verify_level_1_opinion', schema='safety')
    op.drop_column('hazard_reports', 'verify_level_1_at', schema='safety')
    op.drop_column('hazard_reports', 'verify_level_1_by_name', schema='safety')
    op.drop_column('hazard_reports', 'verify_level_1_by', schema='safety')
    op.drop_column('hazard_reports', 'verify_level_1_status', schema='safety')

    # 整改回复字段
    op.drop_column('hazard_reports', 'rectification_replied_by_name', schema='safety')
    op.drop_column('hazard_reports', 'rectification_replied_by', schema='safety')
    op.drop_column('hazard_reports', 'rectification_replied_at', schema='safety')
    op.drop_column('hazard_reports', 'rectification_reply', schema='safety')
