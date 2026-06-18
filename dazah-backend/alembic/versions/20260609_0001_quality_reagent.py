"""质量检验试剂/标准品台账表迁移

Revision ID: quality_reagent_001
Revises: qms_ai_log_001
Create Date: 2026-06-09

创建 qms_reagent_quality 表用于质量检验模块的试剂/标准品管理。
包含试剂标签图片、试剂名称、批号、含量等13个字段。
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'quality_reagent_001'
down_revision = 'qms_ai_log_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建 qms_reagent_quality 表"""
    # 创建质量检验试剂/标准品台账表
    op.create_table(
        'qms_reagent_quality',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        # 试剂标签图片URL数组
        sa.Column('reagent_label_urls', postgresql.ARRAY(sa.Text()), nullable=True, comment='试剂标签图片URL数组'),
        # 试剂基本信息
        sa.Column('reagent_name', sa.String(length=200), nullable=False, comment='试剂名称'),
        sa.Column('arrival_date', sa.Date(), nullable=False, comment='到货日期（默认当天）'),
        sa.Column('production_date', sa.Date(), nullable=True, comment='生产日期（AI识别，默认到货日期+3年）'),
        sa.Column('lot_no', sa.String(length=100), nullable=False, comment='批号'),
        sa.Column('incoming_lot_no', sa.String(length=100), nullable=True, comment='入场批号'),
        sa.Column('expiration_date', sa.Date(), nullable=False, comment='有效期'),
        sa.Column('specification', sa.String(length=100), nullable=True, comment='规格'),
        sa.Column('category', sa.String(length=50), nullable=False, comment='分类（试剂/标准品）'),
        sa.Column('reagent_no', sa.String(length=100), nullable=True, comment='编号'),
        sa.Column('content', sa.String(length=100), nullable=True, comment='含量'),
        sa.Column('manufacturer', sa.String(length=200), nullable=True, comment='生产厂家'),
        # 库存信息
        sa.Column('quantity', sa.Numeric(precision=10, scale=2), nullable=False, comment='数量'),
        sa.Column('unit', sa.String(length=20), nullable=False, comment='单位'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='available', comment='状态'),
        # 审计字段
        sa.Column('created_by', sa.String(length=100), nullable=True, comment='创建人'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, onupdate=sa.text('NOW()'), comment='更新时间'),
        schema='qms'
    )

    # 创建索引
    op.create_index('idx_reagent_quality_reagent_name', 'qms_reagent_quality', ['reagent_name'], schema='qms')
    op.create_index('idx_reagent_quality_lot_no', 'qms_reagent_quality', ['lot_no'], schema='qms')
    op.create_index('idx_reagent_quality_category', 'qms_reagent_quality', ['category'], schema='qms')
    op.create_index('idx_reagent_quality_status', 'qms_reagent_quality', ['status'], schema='qms')
    op.create_index('idx_reagent_quality_arrival_date', 'qms_reagent_quality', ['arrival_date'], schema='qms')
    op.create_index('idx_reagent_quality_expiration_date', 'qms_reagent_quality', ['expiration_date'], schema='qms')


def downgrade() -> None:
    """删除 qms_reagent_quality 表"""
    op.drop_index('idx_reagent_quality_expiration_date', table_name='qms_reagent_quality', schema='qms')
    op.drop_index('idx_reagent_quality_arrival_date', table_name='qms_reagent_quality', schema='qms')
    op.drop_index('idx_reagent_quality_status', table_name='qms_reagent_quality', schema='qms')
    op.drop_index('idx_reagent_quality_category', table_name='qms_reagent_quality', schema='qms')
    op.drop_index('idx_reagent_quality_lot_no', table_name='qms_reagent_quality', schema='qms')
    op.drop_index('idx_reagent_quality_reagent_name', table_name='qms_reagent_quality', schema='qms')
    op.drop_table('qms_reagent_quality', schema='qms')