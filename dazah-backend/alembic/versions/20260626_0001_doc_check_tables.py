"""doc_check tables - 文件合规校验模块数据库设计

生成命令: alembic revision --autogenerate -m "doc_check tables"
执行命令: alembic upgrade head
回滚命令: alembic downgrade -1
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '20260626_0001'
down_revision = '20260623_0001'  # 回滚时使用的上一个迁移
depends_on = None


def upgrade():
    """文件合规校验模块 - 4张核心表"""

    # === 1. 系统配置表 (doc_check_config) ===
    op.create_table(
        'doc_check_config',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('config_key', sa.String(100), nullable=False, unique=True),
        sa.Column('config_value', sa.Text()),
        sa.Column('description', sa.String(500)),
        sa.Column('category', sa.String(50)),  # 'threshold' | 'cache' | 'schedule' | 'model'
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_by', sa.String(100)),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_by', sa.String(100)),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        comment='文件合规校验系统配置表'
    )
    # 索引
    op.create_index('ix_doc_check_config_key', 'doc_check_config', ['config_key'])
    op.create_index('ix_doc_check_config_category', 'doc_check_config', ['category'])

    # === 2. AI校验主记录表 (doc_check_main) ===
    op.create_table(
        'doc_check_main',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('file_code', sa.String(100), nullable=False, index=True),  # 文件编号
        sa.Column('file_name', sa.String(500)),  # 文件名称
        sa.Column('file_version', sa.String(50)),  # 文件版本
        sa.Column('file_type', sa.String(50)),  # SOP | 管理规程 | 技术标准 | 质量制度
        sa.Column('check_type', sa.String(50)),  # 校验类型: duplication | conflict | regulation | internal
        sa.Column('file_hash', sa.String(64)),  # MD5指纹
        sa.Column('status', sa.String(20)),  # pending | processing | completed | failed
        sa.Column('overall_risk_level', sa.String(20)),  # high | medium | low | none
        sa.Column('problem_count', sa.Integer(), default=0),
        sa.Column('check_duration_ms', sa.Integer()),  # 校验耗时(毫秒)
        sa.Column('tokens_used', sa.Integer()),  # Token消耗
        sa.Column('operator', sa.String(100)),  # 操作人
        sa.Column('operator_name', sa.String(100)),  # 操作人姓名
        sa.Column('report_url', sa.String(500)),  # PDF报告URL
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.Column('created_by', sa.String(100)),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_by', sa.String(100)),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        comment='文件合规校验主记录表'
    )
    # 索引 - 联合索引提升查询速度
    op.create_index('ix_doc_check_main_file_check_time', 'doc_check_main', ['file_code', 'check_type', 'created_at'])
    op.create_index('ix_doc_check_main_status', 'doc_check_main', ['status'])
    op.create_index('ix_doc_check_main_risk', 'doc_check_main', ['overall_risk_level'])

    # === 3. AI校验问题明细表 (doc_check_problem) ===
    op.create_table(
        'doc_check_problem',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('main_id', sa.String(36), sa.ForeignKey('doc_check_main.id'), nullable=False),
        sa.Column('problem_type', sa.String(50)),  # duplication | conflict | regulation | internal | version_expired
        sa.Column('problem_category', sa.String(50)),  # 细分问题分类
        sa.Column('severity', sa.String(20)),  # high | medium | low
        sa.Column('title', sa.String(200)),  # 问题标题
        sa.Column('description', sa.Text()),  # 问题描述
        sa.Column('location', sa.String(200)),  # 位置: 文件位置/段落位置
        sa.Column('content', sa.Text()),  # 问题内容
        sa.Column('source_file', sa.String(100)),  # 来源文件（冲突/重复时）
        sa.Column('source_file_name', sa.String(500)),  # 来源文件名
        sa.Column('similarity', sa.Float()),  # 相似度(0-1)
        sa.Column('regulation_ref', sa.String(200)),  # 法规依据
        sa.Column('suggestion', sa.Text()),  # 整改建议
        sa.Column('handle_status', sa.String(20)),  # pending | fixed | ignored
        sa.Column('ignore_reason', sa.Text()),  # 忽略原因
        sa.Column('handled_by', sa.String(100)),  # 处理人
        sa.Column('handled_at', sa.DateTime()),  # 处理时间
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        comment='文件合规校验问题明细表'
    )
    op.create_index('ix_doc_check_problem_main', 'doc_check_problem', ['main_id'])
    op.create_index('ix_doc_check_problem_type', 'doc_check_problem', ['problem_type'])
    op.create_index('ix_doc_check_problem_status', 'doc_check_problem', ['handle_status'])
    op.create_index('ix_doc_check_problem_severity', 'doc_check_problem', ['severity'])

    # === 4. 文档向量缓存表 (doc_check_vector_cache) ===
    op.create_table(
        'doc_check_vector_cache',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('file_code', sa.String(100), nullable=False),
        sa.Column('file_name', sa.String(500)),
        sa.Column('file_version', sa.String(50)),
        sa.Column('file_type', sa.String(50)),
        sa.Column('content_hash', sa.String(64)),  # 内容MD5
        sa.Column('text_chunks', sa.Text()),  # JSON存储分片内容
        sa.Column('expire_at', sa.DateTime()),  # 过期时间(默认7天)
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        comment='文档向量缓存表'
    )
    op.create_index('ix_doc_check_cache_code_ver', 'doc_check_vector_cache', ['file_code', 'file_version'])
    op.create_index('ix_doc_check_cache_expire', 'doc_check_vector_cache', ['expire_at'])


def downgrade():
    """回滚所有表"""
    op.drop_table('doc_check_vector_cache')
    op.drop_table('doc_check_problem')
    op.drop_table('doc_check_main')
    op.drop_table('doc_check_config')