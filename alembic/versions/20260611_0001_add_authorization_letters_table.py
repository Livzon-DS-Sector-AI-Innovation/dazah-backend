"""add authorization letters table

Revision ID: 20260611_0001
Revises: 20260610_0002
Create Date: 2026-06-11

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260611_0001"
down_revision: Union[str, None] = "20260610_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 创建 registration schema（如果不存在）
    op.execute("CREATE SCHEMA IF NOT EXISTS registration")

    # 创建 authorization_letters 表
    op.create_table(
        "authorization_letters",
        sa.Column("api_company", sa.String(128), nullable=False, server_default="珠海保税区丽珠合成制药有限公司", comment="原料药企业名称"),
        sa.Column("product_name", sa.String(128), nullable=False, comment="产品名称（对照表标准名）"),
        sa.Column("registration_number", sa.String(32), nullable=False, comment="产品登记号"),
        sa.Column("preparation_unit", sa.String(256), nullable=False, comment="制剂单位名称（药品上市许可持有人/申请人）"),
        sa.Column("preparation_name", sa.String(256), nullable=False, comment="制剂名称"),
        sa.Column("administration_route", sa.String(64), nullable=False, comment="给药途径"),
        sa.Column("template_file_key", sa.String(256), nullable=False, comment="模板文件 key"),
        sa.Column("template_file_name", sa.String(256), nullable=True, comment="模板文件名"),
        sa.Column("output_file_key", sa.String(256), nullable=False, comment="生成文件 key"),
        sa.Column("output_file_name", sa.String(256), nullable=False, comment="生成文件名"),
        sa.Column("remarks", sa.Text(), nullable=True, comment="备注"),
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column("updated_by", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default="false"),
        sa.ForeignKeyConstraint(["created_by"], ["identity.users.id"]),
        sa.ForeignKeyConstraint(["updated_by"], ["identity.users.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="registration",
    )

    # 创建索引
    op.create_index("ix_authorization_letters_product_name", "authorization_letters", ["product_name"], schema="registration")
    op.create_index("ix_authorization_letters_registration_number", "authorization_letters", ["registration_number"], schema="registration")


def downgrade() -> None:
    op.drop_index("ix_authorization_letters_registration_number", table_name="authorization_letters", schema="registration")
    op.drop_index("ix_authorization_letters_product_name", table_name="authorization_letters", schema="registration")
    op.drop_table("authorization_letters", schema="registration")
    op.execute("DROP SCHEMA IF EXISTS registration")
