"""创建试剂提醒配置表

Revision ID: 20250630_0001_reagent_reminder_config
Revises: 20250629_0003_ai_config
Create Date: 2026-06-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20250630_0001'
down_revision: Union[str, None] = 'f1ce4c737dbd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS qms.qms_reagent_reminder_config (
            id VARCHAR(36) PRIMARY KEY,
            feishu_app_id VARCHAR(128),
            feishu_app_secret VARCHAR(256),
            feishu_chat_id VARCHAR(128),
            low_stock_threshold INTEGER DEFAULT 2,
            is_enabled BOOLEAN DEFAULT TRUE,
            last_remind_time TIMESTAMP,
            last_remind_content TEXT,
            created_by VARCHAR(64),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        )
    """)
    
    # 添加注释
    op.execute("COMMENT ON TABLE qms.qms_reagent_reminder_config IS '试剂提醒配置表'")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS qms.qms_reagent_reminder_config")