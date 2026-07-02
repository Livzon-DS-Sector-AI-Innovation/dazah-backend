"""static_data tables - 业务静态数据模块数据库设计

12张表：3张基础字典 + 5张实验室台账 + 4张质量标准
生成命令: alembic revision --autogenerate -m "static_data tables"
执行命令: alembic upgrade head
回滚命令: alembic downgrade -1
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '20260628_0001'
down_revision = '20260626_0001'  # 基于 doc_check_tables 迁移
depends_on = None


def upgrade():
    """业务静态数据模块 - 12张核心表"""

    # ========== 一、通用字典表（3张） ==========

    # === 1. 贮存条件字典 t_qs_storage_condition ===
    op.create_table(
        't_qs_storage_condition',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('cond_code', sa.String(50), nullable=False, comment='贮存条件编码(唯一)'),
        sa.Column('cond_name', sa.String(100), nullable=False, comment='贮存条件名称'),
        sa.Column('temp_min', sa.Numeric(5, 2), nullable=True, comment='温度下限(℃)'),
        sa.Column('temp_max', sa.Numeric(5, 2), nullable=True, comment='温度上限(℃)'),
        sa.Column('humidity', sa.String(50), nullable=True, comment='湿度要求'),
        sa.Column('remark', sa.String(500), nullable=True, comment='备注'),
        sa.Column('status', sa.SmallInteger(), nullable=False, server_default='0', comment='状态：0启用 1停用'),
        sa.Column('create_by', sa.BigInteger(), nullable=False, comment='创建人ID'),
        sa.Column('create_time', sa.DateTime(), nullable=False, server_default=sa.func.now(), comment='创建时间'),
        sa.Column('update_by', sa.BigInteger(), nullable=True, comment='更新人ID'),
        sa.Column('update_time', sa.DateTime(), nullable=True, server_default=sa.func.now(), onupdate=sa.func.now(), comment='更新时间'),
        sa.Column('del_flag', sa.SmallInteger(), nullable=False, server_default='0', comment='软删除：0未删 1已删'),
        comment='贮存条件字典'
    )
    op.create_index('ix_t_qs_storage_cond_code', 't_qs_storage_condition', ['cond_code', 'del_flag'], unique=False)

    # === 2. 计量单位字典 t_qs_unit ===
    op.create_table(
        't_qs_unit',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('unit_code', sa.String(50), nullable=False, comment='单位编码(唯一)'),
        sa.Column('unit_name', sa.String(50), nullable=False, comment='单位名称'),
        sa.Column('unit_type', sa.String(30), nullable=False, comment='单位类别：质量/体积/浓度/微生物/比率'),
        sa.Column('base_value', sa.Numeric(20, 6), nullable=True, comment='换算基准值'),
        sa.Column('remark', sa.String(500), nullable=True, comment='备注'),
        sa.Column('status', sa.SmallInteger(), nullable=False, server_default='0', comment='状态：0启用 1停用'),
        sa.Column('create_by', sa.BigInteger(), nullable=False),
        sa.Column('create_time', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('update_by', sa.BigInteger(), nullable=True),
        sa.Column('update_time', sa.DateTime(), nullable=True, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('del_flag', sa.SmallInteger(), nullable=False, server_default='0'),
        comment='计量单位字典'
    )
    op.create_index('ix_t_qs_unit_code', 't_qs_unit', ['unit_code', 'del_flag'], unique=False)

    # === 3. 检验项目字典 t_qs_test_item ===
    op.create_table(
        't_qs_test_item',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('item_code', sa.String(50), nullable=False, comment='检验项目编码(唯一)'),
        sa.Column('item_name', sa.String(100), nullable=False, comment='检验项目名称'),
        sa.Column('item_category', sa.String(30), nullable=False, comment='检验分类：理化/仪器分析/微生物'),
        sa.Column('unit_code', sa.String(50), nullable=False, comment='默认计量单位编码'),
        sa.Column('method_desc', sa.String(500), nullable=True, comment='检验方法简述'),
        sa.Column('sort_num', sa.Integer(), nullable=True, server_default='0', comment='排序号'),
        sa.Column('status', sa.SmallInteger(), nullable=False, server_default='0', comment='0启用 1停用'),
        sa.Column('create_by', sa.BigInteger(), nullable=False),
        sa.Column('create_time', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('update_by', sa.BigInteger(), nullable=True),
        sa.Column('update_time', sa.DateTime(), nullable=True, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('del_flag', sa.SmallInteger(), nullable=False, server_default='0'),
        comment='检验项目字典'
    )
    op.create_index('ix_t_qs_test_item_code', 't_qs_test_item', ['item_code', 'del_flag'], unique=False)

    # ========== 二、实验室资源台账表（5张） ==========

    # === 4. 检测设备台账 t_qs_equipment ===
    op.create_table(
        't_qs_equipment',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('eq_code', sa.String(50), nullable=False, comment='设备内部编号(唯一)'),
        sa.Column('eq_name', sa.String(100), nullable=False, comment='仪器名称'),
        sa.Column('model', sa.String(100), nullable=False, comment='型号'),
        sa.Column('serial_no', sa.String(100), nullable=False, comment='出厂序列号'),
        sa.Column('manufacturer', sa.String(100), nullable=False, comment='生产厂家'),
        sa.Column('lab_id', sa.BigInteger(), nullable=False, comment='所属实验室ID'),
        sa.Column('location', sa.String(100), nullable=False, comment='存放位置'),
        sa.Column('eq_category', sa.String(50), nullable=False, comment='设备分类：色谱类/称量类/灭菌类/微生物类'),
        sa.Column('cal_cycle', sa.Integer(), nullable=False, comment='校准周期(月)'),
        sa.Column('last_cal_date', sa.Date(), nullable=False, comment='上次校准日期'),
        sa.Column('next_cal_date', sa.Date(), nullable=False, comment='下次校准日期(预警字段)'),
        sa.Column('verify_status', sa.String(30), nullable=False, comment='验证状态：已完成/待验证/过期'),
        sa.Column('eq_status', sa.SmallInteger(), nullable=False, server_default='0', comment='设备状态：0在用 1维修 2封存 3报废'),
        sa.Column('manager_id', sa.BigInteger(), nullable=False, comment='设备管理员ID'),
        sa.Column('attach_file', sa.Text(), nullable=True, comment='附件(JSON：校准证书、SOP、验证资料)'),
        sa.Column('remark', sa.String(500), nullable=True, comment='备注'),
        sa.Column('create_by', sa.BigInteger(), nullable=False),
        sa.Column('create_time', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('update_by', sa.BigInteger(), nullable=True),
        sa.Column('update_time', sa.DateTime(), nullable=True, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('del_flag', sa.SmallInteger(), nullable=False, server_default='0'),
        comment='检测设备台账'
    )
    op.create_index('ix_t_qs_equipment_code', 't_qs_equipment', ['eq_code', 'del_flag'], unique=False)
    op.create_index('ix_t_qs_equipment_next_cal', 't_qs_equipment', ['next_cal_date'])

    # === 5. 色谱柱管理 t_qs_chrom_column ===
    op.create_table(
        't_qs_chrom_column',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('col_code', sa.String(50), nullable=False, comment='色谱柱内部编号(唯一)'),
        sa.Column('col_type', sa.String(50), nullable=False, comment='固定相类型(C18/C8等)'),
        sa.Column('spec', sa.String(100), nullable=False, comment='规格参数'),
        sa.Column('manufacturer', sa.String(100), nullable=False, comment='厂家'),
        sa.Column('serial_no', sa.String(100), nullable=False, comment='原厂序列号'),
        sa.Column('purchase_date', sa.Date(), nullable=False, comment='采购日期'),
        sa.Column('use_start_date', sa.Date(), nullable=True, comment='启用日期'),
        sa.Column('max_use_times', sa.Integer(), nullable=False, comment='最大允许使用次数'),
        sa.Column('used_times', sa.Integer(), nullable=False, server_default='0', comment='已使用次数'),
        sa.Column('storage_cond_code', sa.String(50), nullable=False, comment='贮存条件编码'),
        sa.Column('location', sa.String(100), nullable=False, comment='存放位置'),
        sa.Column('col_status', sa.SmallInteger(), nullable=False, server_default='0', comment='0在用 1待清洗 2封存 3报废'),
        sa.Column('apply_method', sa.String(500), nullable=True, comment='适用检测方法'),
        sa.Column('attach_file', sa.Text(), nullable=True, comment='清洗记录、报废审批附件'),
        sa.Column('remark', sa.String(500), nullable=True),
        sa.Column('create_by', sa.BigInteger(), nullable=False),
        sa.Column('create_time', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('update_by', sa.BigInteger(), nullable=True),
        sa.Column('update_time', sa.DateTime(), nullable=True, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('del_flag', sa.SmallInteger(), nullable=False, server_default='0'),
        comment='色谱柱管理'
    )
    op.create_index('ix_t_qs_chrom_col_code', 't_qs_chrom_column', ['col_code', 'del_flag'], unique=False)
    op.create_index('ix_t_qs_chrom_col_used_times', 't_qs_chrom_column', ['used_times'])

    # === 6. 培养基管理 t_qs_medium ===
    op.create_table(
        't_qs_medium',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('medium_code', sa.String(50), nullable=False, comment='培养基编码(唯一)'),
        sa.Column('medium_name', sa.String(100), nullable=False, comment='培养基名称'),
        sa.Column('medium_type', sa.String(50), nullable=False, comment='培养基类型'),
        sa.Column('manufacturer', sa.String(100), nullable=False, comment='生产厂家'),
        sa.Column('batch_no', sa.String(50), nullable=False, comment='厂家批号'),
        sa.Column('spec', sa.String(50), nullable=False, comment='包装规格'),
        sa.Column('storage_cond_code', sa.String(50), nullable=False, comment='贮存条件编码'),
        sa.Column('expire_date', sa.Date(), nullable=False, comment='有效期至(预警字段)'),
        sa.Column('verify_status', sa.String(30), nullable=False, comment='适用性验证状态'),
        sa.Column('config_method', sa.Text(), nullable=True, comment='配制灭菌参数'),
        sa.Column('stock_num', sa.Numeric(20, 4), nullable=False, server_default='0', comment='当前库存数量'),
        sa.Column('unit_code', sa.String(50), nullable=False, comment='库存单位编码'),
        sa.Column('min_stock', sa.Numeric(20, 4), nullable=False, comment='最低安全库存'),
        sa.Column('status', sa.SmallInteger(), nullable=False, server_default='0', comment='0在用 1停用'),
        sa.Column('attach_file', sa.Text(), nullable=True, comment='配制、阴阳对照试验附件'),
        sa.Column('remark', sa.String(500), nullable=True),
        sa.Column('create_by', sa.BigInteger(), nullable=False),
        sa.Column('create_time', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('update_by', sa.BigInteger(), nullable=True),
        sa.Column('update_time', sa.DateTime(), nullable=True, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('del_flag', sa.SmallInteger(), nullable=False, server_default='0'),
        comment='培养基管理'
    )
    op.create_index('ix_t_qs_medium_code', 't_qs_medium', ['medium_code', 'del_flag'], unique=False)
    op.create_index('ix_t_qs_medium_expire', 't_qs_medium', ['expire_date'])

    # === 7. 试剂管理 t_qs_reagent ===
    op.create_table(
        't_qs_reagent',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('reagent_code', sa.String(50), nullable=False, comment='试剂编码(唯一)'),
        sa.Column('reagent_name', sa.String(100), nullable=False, comment='试剂名称'),
        sa.Column('cas_no', sa.String(50), nullable=False, comment='CAS号'),
        sa.Column('purity', sa.String(30), nullable=False, comment='纯度级别(AR/GR/CP)'),
        sa.Column('manufacturer', sa.String(100), nullable=False, comment='厂家'),
        sa.Column('batch_no', sa.String(50), nullable=False, comment='试剂批号'),
        sa.Column('spec', sa.String(50), nullable=False, comment='包装规格'),
        sa.Column('danger_type', sa.String(50), nullable=False, comment='危险分类：普通/易制毒/剧毒等'),
        sa.Column('storage_cond_code', sa.String(50), nullable=False, comment='贮存条件编码'),
        sa.Column('expire_date', sa.Date(), nullable=False, comment='有效期至'),
        sa.Column('stock_num', sa.Numeric(20, 4), nullable=False, comment='当前库存'),
        sa.Column('unit_code', sa.String(50), nullable=False, comment='库存单位'),
        sa.Column('min_stock', sa.Numeric(20, 4), nullable=False, comment='最低安全库存'),
        sa.Column('store_location', sa.String(100), nullable=False, comment='存放库位'),
        sa.Column('attach_file', sa.Text(), nullable=True, comment='MSDS、COA附件'),
        sa.Column('status', sa.SmallInteger(), nullable=False, server_default='0', comment='0启用 1停用'),
        sa.Column('remark', sa.String(500), nullable=True),
        sa.Column('create_by', sa.BigInteger(), nullable=False),
        sa.Column('create_time', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('update_by', sa.BigInteger(), nullable=True),
        sa.Column('update_time', sa.DateTime(), nullable=True, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('del_flag', sa.SmallInteger(), nullable=False, server_default='0'),
        comment='试剂管理'
    )
    op.create_index('ix_t_qs_reagent_code', 't_qs_reagent', ['reagent_code', 'del_flag'], unique=False)
    op.create_index('ix_t_qs_reagent_expire', 't_qs_reagent', ['expire_date'])

    # === 8. 标准物质管理 t_qs_standard_material ===
    op.create_table(
        't_qs_standard_material',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('std_code', sa.String(50), nullable=False, comment='标准品内部编码(唯一)'),
        sa.Column('std_name', sa.String(100), nullable=False, comment='标准品名称'),
        sa.Column('cas_no', sa.String(50), nullable=True, comment='CAS号'),
        sa.Column('manufacturer', sa.String(100), nullable=False, comment='厂家'),
        sa.Column('batch_no', sa.String(50), nullable=False, comment='厂家批号'),
        sa.Column('cert_no', sa.String(100), nullable=False, comment='溯源证书编号'),
        sa.Column('purity', sa.Numeric(20, 6), nullable=False, comment='纯度含量'),
        sa.Column('init_stock', sa.Numeric(20, 4), nullable=False, comment='初始入库量'),
        sa.Column('remain_stock', sa.Numeric(20, 4), nullable=False, comment='剩余库存(首页预警核心字段)'),
        sa.Column('unit_code', sa.String(50), nullable=False, comment='库存单位编码'),
        sa.Column('storage_cond_code', sa.String(50), nullable=False, comment='贮存条件编码'),
        sa.Column('expire_date', sa.Date(), nullable=False, comment='有效期至'),
        sa.Column('store_location', sa.String(100), nullable=False, comment='存放位置'),
        sa.Column('std_type', sa.String(50), nullable=False, comment='标准品类型：法定/工作/自制'),
        sa.Column('recal_cycle', sa.Integer(), nullable=True, comment='复标周期(月)'),
        sa.Column('min_stock', sa.Numeric(20, 4), nullable=False, comment='最低安全库存'),
        sa.Column('attach_file', sa.Text(), nullable=True, comment='证书、复标记录附件'),
        sa.Column('status', sa.SmallInteger(), nullable=False, comment='0在用 1封存 2报废'),
        sa.Column('remark', sa.String(500), nullable=True),
        sa.Column('create_by', sa.BigInteger(), nullable=False),
        sa.Column('create_time', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('update_by', sa.BigInteger(), nullable=True),
        sa.Column('update_time', sa.DateTime(), nullable=True, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('del_flag', sa.SmallInteger(), nullable=False, server_default='0'),
        comment='标准物质管理'
    )
    op.create_index('ix_t_qs_std_mat_code', 't_qs_standard_material', ['std_code', 'del_flag'], unique=False)
    op.create_index('ix_t_qs_std_mat_expire', 't_qs_standard_material', ['expire_date'])

    # ========== 三、质量标准主表+明细表（4张） ==========

    # === 9. 物料质量标准主表 t_qs_material_standard ===
    op.create_table(
        't_qs_material_standard',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('material_code', sa.String(50), nullable=False, comment='物料编码'),
        sa.Column('material_name', sa.String(100), nullable=False, comment='物料名称'),
        sa.Column('material_type', sa.String(50), nullable=False, comment='物料类别：原料/辅料/包材/中间体'),
        sa.Column('spec', sa.String(100), nullable=False, comment='物料规格'),
        sa.Column('supplier_id', sa.BigInteger(), nullable=True, comment='供应商ID'),
        sa.Column('standard_source', sa.String(50), nullable=False, comment='标准来源：中国药典/USP/内控'),
        sa.Column('standard_no', sa.String(50), nullable=False, comment='标准编号'),
        sa.Column('version', sa.String(20), nullable=False, comment='版本号'),
        sa.Column('storage_cond_code', sa.String(50), nullable=False, comment='贮存条件编码'),
        sa.Column('status', sa.SmallInteger(), nullable=False, server_default='0', comment='0草稿 1待审核 2已生效 3已作废'),
        sa.Column('draft_user', sa.BigInteger(), nullable=False, comment='起草人ID'),
        sa.Column('audit_user', sa.BigInteger(), nullable=True, comment='审核人ID'),
        sa.Column('approve_user', sa.BigInteger(), nullable=True, comment='批准人ID'),
        sa.Column('effect_date', sa.Date(), nullable=True, comment='生效日期'),
        sa.Column('invalid_date', sa.Date(), nullable=True, comment='作废日期'),
        sa.Column('attach_file', sa.Text(), nullable=True, comment='标准PDF、验证资料附件'),
        sa.Column('remark', sa.String(500), nullable=True),
        sa.Column('create_by', sa.BigInteger(), nullable=False),
        sa.Column('create_time', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('update_by', sa.BigInteger(), nullable=True),
        sa.Column('update_time', sa.DateTime(), nullable=True, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('del_flag', sa.SmallInteger(), nullable=False, server_default='0'),
        comment='物料质量标准主表'
    )
    op.create_index('ix_t_qs_mat_std_code', 't_qs_material_standard', ['material_code', 'del_flag'], unique=False)
    op.create_index('ix_t_qs_mat_std_version', 't_qs_material_standard', ['material_code', 'version', 'del_flag'], unique=False)

    # === 10. 物料质量标准明细表 t_qs_material_standard_item ===
    op.create_table(
        't_qs_material_standard_item',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('standard_id', sa.BigInteger(), nullable=False, comment='关联物料标准主表ID'),
        sa.Column('item_code', sa.String(50), nullable=False, comment='检验项目编码'),
        sa.Column('test_method', sa.String(500), nullable=True, comment='检验方法'),
        sa.Column('limit_type', sa.String(30), nullable=False, comment='限度类型：上限/下限/区间/不得检出'),
        sa.Column('limit_min', sa.Numeric(30, 10), nullable=True, comment='下限值'),
        sa.Column('limit_max', sa.Numeric(30, 10), nullable=True, comment='上限值'),
        sa.Column('is_release_item', sa.SmallInteger(), nullable=False, server_default='0', comment='是否放行必检项：0否 1是'),
        sa.Column('sort_num', sa.Integer(), nullable=True, server_default='0', comment='排序号'),
        sa.Column('create_by', sa.BigInteger(), nullable=False),
        sa.Column('create_time', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('del_flag', sa.SmallInteger(), nullable=False, server_default='0'),
        comment='物料质量标准-检验项目明细'
    )
    op.create_index('ix_t_qs_mat_std_item_std_id', 't_qs_material_standard_item', ['standard_id'])

    # === 11. 产品质量标准主表 t_qs_product_standard ===
    op.create_table(
        't_qs_product_standard',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('product_code', sa.String(50), nullable=False, comment='产品编码'),
        sa.Column('product_name', sa.String(100), nullable=False, comment='产品通用名'),
        sa.Column('trade_name', sa.String(100), nullable=True, comment='商品名'),
        sa.Column('spec', sa.String(100), nullable=False, comment='产品规格'),
        sa.Column('dosage_form', sa.String(50), nullable=False, comment='剂型'),
        sa.Column('reg_standard_no', sa.String(100), nullable=False, comment='注册标准号'),
        sa.Column('inner_standard_no', sa.String(50), nullable=False, comment='内控标准编号'),
        sa.Column('version', sa.String(20), nullable=False, comment='版本号'),
        sa.Column('storage_cond_code', sa.String(50), nullable=False, comment='贮存条件编码'),
        sa.Column('valid_period', sa.Integer(), nullable=False, comment='产品有效期(月)'),
        sa.Column('pack_spec', sa.String(100), nullable=False, comment='包装规格'),
        sa.Column('status', sa.SmallInteger(), nullable=False, server_default='0', comment='0草稿 1待审核 2已生效 3已作废'),
        sa.Column('draft_user', sa.BigInteger(), nullable=False, comment='起草人ID'),
        sa.Column('audit_user', sa.BigInteger(), nullable=True, comment='审核人ID'),
        sa.Column('approve_user', sa.BigInteger(), nullable=True, comment='批准人ID'),
        sa.Column('effect_date', sa.Date(), nullable=True, comment='生效日期'),
        sa.Column('invalid_date', sa.Date(), nullable=True, comment='作废日期'),
        sa.Column('attach_file', sa.Text(), nullable=True, comment='注册标准、验证资料附件'),
        sa.Column('remark', sa.String(500), nullable=True),
        sa.Column('create_by', sa.BigInteger(), nullable=False),
        sa.Column('create_time', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('update_by', sa.BigInteger(), nullable=True),
        sa.Column('update_time', sa.DateTime(), nullable=True, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('del_flag', sa.SmallInteger(), nullable=False, server_default='0'),
        comment='产品质量标准主表'
    )
    op.create_index('ix_t_qs_prod_std_code', 't_qs_product_standard', ['product_code', 'del_flag'], unique=False)
    op.create_index('ix_t_qs_prod_std_version', 't_qs_product_standard', ['product_code', 'version', 'del_flag'], unique=False)

    # === 12. 产品质量标准明细表 t_qs_product_standard_item ===
    op.create_table(
        't_qs_product_standard_item',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('standard_id', sa.BigInteger(), nullable=False, comment='关联产品标准主表ID'),
        sa.Column('item_code', sa.String(50), nullable=False, comment='检验项目编码'),
        sa.Column('test_method', sa.String(500), nullable=True, comment='检验方法'),
        sa.Column('legal_limit_min', sa.Numeric(30, 10), nullable=True, comment='法定下限'),
        sa.Column('legal_limit_max', sa.Numeric(30, 10), nullable=True, comment='法定上限'),
        sa.Column('inner_limit_min', sa.Numeric(30, 10), nullable=True, comment='内控下限'),
        sa.Column('inner_limit_max', sa.Numeric(30, 10), nullable=True, comment='内控上限'),
        sa.Column('is_release_item', sa.SmallInteger(), nullable=False, server_default='0', comment='是否放行关键项'),
        sa.Column('sort_num', sa.Integer(), nullable=True, server_default='0', comment='排序号'),
        sa.Column('create_by', sa.BigInteger(), nullable=False),
        sa.Column('create_time', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('del_flag', sa.SmallInteger(), nullable=False, server_default='0'),
        comment='产品质量标准-检验项目明细'
    )
    op.create_index('ix_t_qs_prod_std_item_std_id', 't_qs_product_standard_item', ['standard_id'])


def downgrade():
    """回滚所有12张表"""
    op.drop_table('t_qs_product_standard_item')
    op.drop_table('t_qs_product_standard')
    op.drop_table('t_qs_material_standard_item')
    op.drop_table('t_qs_material_standard')
    op.drop_table('t_qs_standard_material')
    op.drop_table('t_qs_reagent')
    op.drop_table('t_qs_medium')
    op.drop_table('t_qs_chrom_column')
    op.drop_table('t_qs_equipment')
    op.drop_table('t_qs_test_item')
    op.drop_table('t_qs_unit')
    op.drop_table('t_qs_storage_condition')