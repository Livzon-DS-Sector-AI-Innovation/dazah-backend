"""hplc_reference_substance - 液相色谱对照品台账

液相色谱分析用的对照品管理表，包含开瓶日期、COA状态等特殊字段
生成命令: alembic revision --autogenerate -m "hplc_reference_substance"
执行命令: alembic upgrade head
回滚命令: alembic downgrade -1
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '20260629_0001'
down_revision = '20260628_0001'  # 基于 static_data_tables 迁移
depends_on = None


def upgrade():
    """液相色谱对照品台账表"""
    op.create_table(
        't_qs_hplc_reference',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('ref_code', sa.String(50), nullable=False, comment='对照品内部编号(唯一)'),
        sa.Column('ref_name', sa.String(200), nullable=False, comment='对照品名称'),
        sa.Column('project_name', sa.String(100), nullable=True, comment='关联检测项目'),
        sa.Column('internal_batch', sa.String(50), nullable=True, comment='厂内批号'),
        sa.Column('cas_no', sa.String(50), nullable=True, comment='CAS号'),
        sa.Column('cat_no', sa.String(50), nullable=True, comment='供应商货号CAT NO'),
        sa.Column('manufacturer_batch', sa.String(50), nullable=True, comment='厂家批号'),
        sa.Column('manufacturer', sa.String(200), nullable=True, comment='供应商/来源'),
        sa.Column('spec', sa.String(50), nullable=True, comment='规格/瓶'),
        sa.Column('purity', sa.Numeric(10, 4), nullable=True, comment='纯度'),
        sa.Column('content', sa.Numeric(10, 4), nullable=True, comment='含量'),
        sa.Column('quantity', sa.Integer(), nullable=True, comment='数量'),
        sa.Column('stock_status', sa.String(100), nullable=True, comment='现有库存状态'),
        sa.Column('arrival_date', sa.Date(), nullable=True, comment='到货日期'),
        sa.Column('produce_date', sa.Date(), nullable=True, comment='生产/标定日期'),
        sa.Column('expire_date', sa.Date(), nullable=True, comment='有效期至'),
        sa.Column('recal_cycle_days', sa.Integer(), nullable=True, comment='复标周期(天)'),
        sa.Column('open_date', sa.Date(), nullable=True, comment='开瓶日期'),
        sa.Column('open_expire_days', sa.Integer(), nullable=True, comment='开瓶有效期(天)'),
        sa.Column('storage_cond_code', sa.String(50), nullable=True, comment='贮存条件编码'),
        sa.Column('location', sa.String(100), nullable=True, comment='存放位置'),
        sa.Column('has_coa', sa.Boolean(), nullable=True, server_default='false', comment='是否有COA'),
        sa.Column('handover_no', sa.String(100), nullable=True, comment='交接单号'),
        sa.Column('ref_status', sa.SmallInteger(), nullable=False, server_default='0', comment='状态：0在用 1用完 2过期 3报废'),
        sa.Column('remark', sa.String(500), nullable=True, comment='备注'),
        sa.Column('attach_file', sa.Text(), nullable=True, comment='附件JSON(COA、复标记录等)'),
        sa.Column('create_by', sa.BigInteger(), nullable=False, comment='创建人ID'),
        sa.Column('create_time', sa.DateTime(), nullable=False, server_default=sa.func.now(), comment='创建时间'),
        sa.Column('update_by', sa.BigInteger(), nullable=True, comment='更新人ID'),
        sa.Column('update_time', sa.DateTime(), nullable=True, server_default=sa.func.now(), onupdate=sa.func.now(), comment='更新时间'),
        sa.Column('del_flag', sa.SmallInteger(), nullable=False, server_default='0', comment='软删除：0未删 1已删'),
        comment='液相色谱对照品台账'
    )
    op.create_index('ix_t_qs_hplc_ref_code', 't_qs_hplc_reference', ['ref_code', 'del_flag'], unique=False)
    op.create_index('ix_t_qs_hplc_ref_expire', 't_qs_hplc_reference', ['expire_date'])
    op.create_index('ix_t_qs_hplc_ref_project', 't_qs_hplc_reference', ['project_name'])


def downgrade():
    """回滚液相色谱对照品台账表"""
    op.drop_index('ix_t_qs_hplc_ref_project', 't_qs_hplc_reference')
    op.drop_index('ix_t_qs_hplc_ref_expire', 't_qs_hplc_reference')
    op.drop_index('ix_t_qs_hplc_ref_code', 't_qs_hplc_reference')
    op.drop_table('t_qs_hplc_reference')