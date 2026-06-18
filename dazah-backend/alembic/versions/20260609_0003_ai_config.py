"""AI 配置表迁移

Revision ID: ai_config_001
Revises: quality_reagent_001
Create Date: 2026-06-09 11:10:00

"""
from typing import Sequence, Any
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ai_config_001'
down_revision: str = 'quality_reagent_001'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 创建 AI 配置表
    op.create_table(
        'qms_ai_config',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('config_key', sa.String(100), nullable=False, unique=True),
        sa.Column('config_value', sa.Text(), nullable=True),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema='qms'
    )

    # 插入默认 AI 配置
    default_config = {
        "minimax_api_key": "",
        "minimax_base_url": "https://api.minimaxi.com/v1",
        "minimax_text_model": "MiniMax-M2.7",
        "minimax_vision_model": "MiniMax-M3",
        "enable_ai_reason": True,
        "enable_ai_scrap": True,
        "enable_ai_analyse": True,
        "enable_ai_label_recognize": True,
        "temperature": 0.7,
        "max_tokens": 1024,
        "timeout": 60,
    }

    import json
    op.execute(
        "INSERT INTO qms.qms_ai_config (id, config_key, config_value, description) "
        "VALUES (gen_random_uuid(), 'ai_config', '{}', 'AI系统配置')".format(
            json.dumps(default_config).replace("'", "''")
        )
    )


def downgrade() -> None:
    op.drop_table('qms_ai_config', schema='qms')