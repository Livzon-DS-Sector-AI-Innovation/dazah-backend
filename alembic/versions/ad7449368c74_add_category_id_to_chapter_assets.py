"""add_category_id_to_chapter_assets

Revision ID: ad7449368c74
Revises: 20260616_0001
Create Date: 2026-06-17 11:08:13.950695
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'ad7449368c74'
down_revision: Union[str, None] = '20260616_0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('chapter_assets', sa.Column('category_id', sa.UUID(), nullable=True, comment='素材分类ID'), schema='dossier_writer')
    op.create_foreign_key(
        'fk_chapter_assets_category_id',
        'chapter_assets', 'asset_categories',
        ['category_id'], ['id'],
        source_schema='dossier_writer', referent_schema='dossier_writer',
        ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_constraint('fk_chapter_assets_category_id', 'chapter_assets', schema='dossier_writer', type_='foreignkey')
    op.drop_column('chapter_assets', 'category_id', schema='dossier_writer')
