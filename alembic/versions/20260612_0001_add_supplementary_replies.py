"""add supplementary_replies table

Revision ID: 20260612_0001
Revises: ec4654a030c0
Create Date: 2026-06-12 10:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260612_0001'
down_revision = 'ec4654a030c0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'supplementary_replies',
        sa.Column('drug_name', sa.String(length=128), nullable=False, comment='药品名称'),
        sa.Column('registration_number', sa.String(length=32), nullable=True, comment='登记号'),
        sa.Column('acceptance_number', sa.String(length=64), nullable=True, comment='受理号'),
        sa.Column('company_name', sa.String(length=256), nullable=True, comment='申请人/公司名称'),
        sa.Column('notice_file_key', sa.String(length=256), nullable=False, comment='CDE通知函文件 key'),
        sa.Column('notice_file_name', sa.String(length=256), nullable=True, comment='CDE通知函文件名'),
        sa.Column('template_file_key', sa.String(length=256), nullable=True, comment='公司模板文件 key'),
        sa.Column('template_file_name', sa.String(length=256), nullable=True, comment='公司模板文件名'),
        sa.Column('output_file_key', sa.String(length=256), nullable=False, comment='生成文件 key'),
        sa.Column('output_file_name', sa.String(length=256), nullable=False, comment='生成文件名'),
        sa.Column('question_count', sa.Integer(), nullable=False, server_default='0', comment='提取的问题数量'),
        sa.Column('remarks', sa.Text(), nullable=True, comment='备注'),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.ForeignKeyConstraint(['created_by'], ['identity.users.id']),
        sa.ForeignKeyConstraint(['updated_by'], ['identity.users.id']),
        sa.PrimaryKeyConstraint('id'),
        schema='registration'
    )
    op.create_index('ix_supplementary_replies_drug_name', 'supplementary_replies', ['drug_name'], schema='registration')
    op.create_index('ix_supplementary_replies_registration_number', 'supplementary_replies', ['registration_number'], schema='registration')


def downgrade() -> None:
    op.drop_index('ix_supplementary_replies_registration_number', table_name='supplementary_replies', schema='registration')
    op.drop_index('ix_supplementary_replies_drug_name', table_name='supplementary_replies', schema='registration')
    op.drop_table('supplementary_replies', schema='registration')
