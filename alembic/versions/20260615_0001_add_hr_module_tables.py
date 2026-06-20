"""add hr module tables

Revision ID: 20260615_0001_hr
Revises: b1a51f063719
Create Date: 2026-06-15
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260615_0001_hr"
down_revision: Union[str, None] = "b1a51f063719"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    from sqlalchemy import inspect
    conn = op.get_bind()
    insp = inspect(conn)
    if "departments" in [t for t in insp.get_table_names(schema="hr")]:
        return  # tables already created by initial schema
    op.execute("CREATE SCHEMA IF NOT EXISTS hr")

    op.create_table(
        "departments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("name", sa.String(64), nullable=False, comment="部门名称"),
        sa.Column("code", sa.String(32), nullable=False, comment="部门编码"),
        sa.Column("description", sa.String(256), nullable=True, comment="部门描述"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
        schema="hr",
    )
    op.create_index("ix_departments_code", "departments", ["code"], schema="hr")

    op.create_table(
        "teams",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("name", sa.String(64), nullable=False, comment="班组名称"),
        sa.Column("code", sa.String(32), nullable=True, comment="班组编码"),
        sa.Column("description", sa.String(256), nullable=True, comment="班组描述"),
        sa.Column("department_id", sa.Uuid(), nullable=False, comment="所属部门ID"),
        sa.ForeignKeyConstraint(["department_id"], ["hr.departments.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="hr",
    )
    op.create_index("ix_teams_department_id", "teams", ["department_id"], schema="hr")
    op.create_index("ix_teams_name", "teams", ["name"], schema="hr")

    op.create_table(
        "employees",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("employee_number", sa.String(32), nullable=False, comment="工号"),
        sa.Column("name", sa.String(64), nullable=False, comment="姓名"),
        sa.Column("domain_account", sa.String(128), nullable=True, comment="域账号"),
        sa.Column("department", sa.String(64), nullable=True, comment="部门"),
        sa.Column("team", sa.String(64), nullable=True, comment="班组"),
        sa.Column("position", sa.String(64), nullable=True, comment="职位"),
        sa.Column("job_category", sa.String(64), nullable=True, comment="岗位类别"),
        sa.Column("level", sa.String(32), nullable=True, comment="职级"),
        sa.Column("qualifications", sa.JSON(), nullable=True, comment="资质证书"),
        sa.Column("qualification_type", sa.String(64), nullable=True, comment="资质类型"),
        sa.Column("gender", sa.String(16), nullable=True, comment="性别"),
        sa.Column("native_place", sa.String(128), nullable=True, comment="籍贯"),
        sa.Column("political_status", sa.String(32), nullable=True, comment="政治面貌"),
        sa.Column("marital_status", sa.String(128), nullable=True, comment="婚姻状况"),
        sa.Column("household_type", sa.String(128), nullable=True, comment="户口类型"),
        sa.Column("status_category", sa.String(32), nullable=True, comment="人员类别"),
        sa.Column("birth_year", sa.Integer(), nullable=True, comment="出生年份"),
        sa.Column("birth_month", sa.Integer(), nullable=True, comment="出生月份"),
        sa.Column("birth_day", sa.Integer(), nullable=True, comment="出生日期"),
        sa.Column("age", sa.Integer(), nullable=True, comment="年龄"),
        sa.Column("work_start_date", sa.Date(), nullable=True, comment="参加工作时间"),
        sa.Column("factory_entry_date", sa.Date(), nullable=True, comment="入厂时间"),
        sa.Column("livo_entry_date", sa.Date(), nullable=True, comment="入丽珠时间"),
        sa.Column("hire_date", sa.Date(), nullable=True, comment="入职时间"),
        sa.Column("graduation_date", sa.Date(), nullable=True, comment="毕业时间"),
        sa.Column("work_years", sa.Integer(), nullable=True, comment="工龄"),
        sa.Column("factory_tenure", sa.Integer(), nullable=True, comment="厂龄"),
        sa.Column("company_tenure", sa.Integer(), nullable=True, comment="司龄"),
        sa.Column("education", sa.String(64), nullable=True, comment="学历"),
        sa.Column("classification", sa.String(64), nullable=True, comment="学历类别"),
        sa.Column("school", sa.String(128), nullable=True, comment="毕业学校"),
        sa.Column("major", sa.String(128), nullable=True, comment="专业"),
        sa.Column("id_card", sa.String(32), nullable=True, comment="身份证号"),
        sa.Column("id_card_expiry", sa.Date(), nullable=True, comment="身份证有效期"),
        sa.Column("id_card_address", sa.String(256), nullable=True, comment="身份证地址"),
        sa.Column("current_address", sa.String(256), nullable=True, comment="现住地址"),
        sa.Column("contract_type", sa.String(32), nullable=True, comment="合同类型"),
        sa.Column("contract_start_date", sa.Date(), nullable=True, comment="合同开始日期"),
        sa.Column("contract_end_date", sa.Date(), nullable=True, comment="合同结束日期"),
        sa.Column("contract_start_date_2", sa.Date(), nullable=True),
        sa.Column("contract_end_date_2", sa.Date(), nullable=True),
        sa.Column("contract_start_date_3", sa.Date(), nullable=True),
        sa.Column("contract_end_date_3", sa.Date(), nullable=True),
        sa.Column("contract_start_date_4", sa.Date(), nullable=True),
        sa.Column("contract_end_date_4", sa.Date(), nullable=True),
        sa.Column("phone", sa.String(32), nullable=True, comment="手机号"),
        sa.Column("email", sa.String(128), nullable=True, comment="邮箱"),
        sa.Column("emergency_contact_name", sa.String(64), nullable=True, comment="紧急联系人"),
        sa.Column("emergency_contact_phone", sa.String(32), nullable=True, comment="紧急联系人电话"),
        sa.Column("emergency_contact_name_2", sa.String(64), nullable=True),
        sa.Column("emergency_contact_phone_2", sa.String(32), nullable=True),
        sa.Column("bank_account", sa.String(64), nullable=True, comment="银行卡号"),
        sa.Column("bank_name", sa.String(64), nullable=True, comment="开户行"),
        sa.Column("training_id", sa.String(64), nullable=True, comment="培训编号"),
        sa.Column("transfer_history", sa.String(512), nullable=True, comment="调动记录"),
        sa.Column("remarks", sa.JSON(), nullable=True, comment="备注"),
        sa.Column("status", sa.String(16), nullable=False, server_default="在职", comment="状态"),
        sa.Column("feishu_open_id", sa.String(64), nullable=True, comment="飞书 Open ID"),
        sa.Column("feishu_record_id", sa.String(64), nullable=True, comment="飞书记录 ID"),
        sa.Column("feishu_synced_at", sa.Date(), nullable=True, comment="飞书最后同步日期"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("employee_number"),
        schema="hr",
    )
    op.create_index("ix_employees_department", "employees", ["department"], schema="hr")
    op.create_index("ix_employees_status", "employees", ["status"], schema="hr")
    op.create_index("ix_employees_name", "employees", ["name"], schema="hr")

    op.create_table(
        "offboarding_records",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("employee_id", sa.Uuid(), nullable=False, comment="员工ID"),
        sa.Column("offboarding_date", sa.Date(), nullable=True, comment="离职日期"),
        sa.Column("offboarding_type", sa.String(32), nullable=True, comment="离职类型"),
        sa.Column("reason", sa.String(256), nullable=True, comment="离职原因"),
        sa.Column("handover_status", sa.String(32), nullable=True, server_default="待交接", comment="交接状态"),
        sa.Column("notes", sa.String(512), nullable=True, comment="备注"),
        sa.ForeignKeyConstraint(["employee_id"], ["hr.employees.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="hr",
    )

    op.create_table(
        "onboarding_records",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("seq_number", sa.String(32), nullable=True),
        sa.Column("employee_number", sa.String(32), nullable=True, comment="工号"),
        sa.Column("name", sa.String(64), nullable=True, comment="姓名"),
        sa.Column("domain_account", sa.String(128), nullable=True),
        sa.Column("department", sa.String(64), nullable=True),
        sa.Column("team", sa.String(64), nullable=True),
        sa.Column("position", sa.String(64), nullable=True),
        sa.Column("job_category", sa.String(64), nullable=True),
        sa.Column("status_category", sa.String(32), nullable=True),
        sa.Column("is_employed", sa.Boolean(), nullable=True),
        sa.Column("hire_date", sa.Date(), nullable=True),
        sa.Column("factory_entry_date", sa.Date(), nullable=True),
        sa.Column("livo_entry_date", sa.Date(), nullable=True),
        sa.Column("work_start_date", sa.Date(), nullable=True),
        sa.Column("graduation_date", sa.Date(), nullable=True),
        sa.Column("birth_month", sa.Integer(), nullable=True),
        sa.Column("birth_day", sa.Integer(), nullable=True),
        sa.Column("contract_type", sa.String(32), nullable=True),
        sa.Column("contract_start_date", sa.Date(), nullable=True),
        sa.Column("contract_end_date", sa.Date(), nullable=True),
        sa.Column("contract_start_date_2", sa.Date(), nullable=True),
        sa.Column("contract_end_date_2", sa.Date(), nullable=True),
        sa.Column("contract_start_date_3", sa.Date(), nullable=True),
        sa.Column("contract_end_date_3", sa.Date(), nullable=True),
        sa.Column("contract_start_date_4", sa.Date(), nullable=True),
        sa.Column("contract_end_date_4", sa.Date(), nullable=True),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("work_years", sa.Integer(), nullable=True),
        sa.Column("factory_tenure", sa.Integer(), nullable=True),
        sa.Column("company_tenure", sa.Integer(), nullable=True),
        sa.Column("hire_month", sa.String(16), nullable=True),
        sa.Column("school", sa.String(128), nullable=True),
        sa.Column("education", sa.String(64), nullable=True),
        sa.Column("major", sa.String(128), nullable=True),
        sa.Column("classification", sa.String(64), nullable=True),
        sa.Column("id_card", sa.String(32), nullable=True),
        sa.Column("id_card_expiry", sa.Date(), nullable=True),
        sa.Column("id_card_address", sa.String(256), nullable=True),
        sa.Column("current_address", sa.String(256), nullable=True),
        sa.Column("marital_status", sa.String(128), nullable=True),
        sa.Column("household_type", sa.String(128), nullable=True),
        sa.Column("political_status", sa.String(32), nullable=True),
        sa.Column("phone", sa.String(32), nullable=True),
        sa.Column("email", sa.String(128), nullable=True),
        sa.Column("emergency_contact_name", sa.String(64), nullable=True),
        sa.Column("emergency_contact_phone", sa.String(32), nullable=True),
        sa.Column("emergency_contact_name_2", sa.String(64), nullable=True),
        sa.Column("emergency_contact_phone_2", sa.String(32), nullable=True),
        sa.Column("bank_account", sa.String(64), nullable=True),
        sa.Column("bank_name", sa.String(64), nullable=True),
        sa.Column("training_id", sa.String(64), nullable=True),
        sa.Column("transfer_history", sa.String(512), nullable=True),
        sa.Column("remarks", sa.JSON(), nullable=True),
        sa.Column("feishu_record_id", sa.String(64), nullable=True),
        sa.Column("feishu_synced_at", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="hr",
    )

    op.create_table(
        "departure_records",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("name", sa.String(64), nullable=True),
        sa.Column("department", sa.String(64), nullable=True),
        sa.Column("team", sa.String(64), nullable=True),
        sa.Column("position", sa.String(64), nullable=True),
        sa.Column("job_category", sa.String(64), nullable=True),
        sa.Column("gender", sa.String(16), nullable=True),
        sa.Column("status_category", sa.String(32), nullable=True),
        sa.Column("livo_entry_date", sa.Date(), nullable=True),
        sa.Column("factory_entry_date", sa.Date(), nullable=True),
        sa.Column("work_start_date", sa.Date(), nullable=True),
        sa.Column("offboarding_date", sa.Date(), nullable=True),
        sa.Column("company_tenure_at_leave", sa.Integer(), nullable=True),
        sa.Column("education", sa.String(64), nullable=True),
        sa.Column("school", sa.String(128), nullable=True),
        sa.Column("major", sa.String(128), nullable=True),
        sa.Column("classification", sa.String(64), nullable=True),
        sa.Column("id_card", sa.String(32), nullable=True),
        sa.Column("native_place", sa.String(128), nullable=True),
        sa.Column("household_type", sa.String(128), nullable=True),
        sa.Column("marital_status", sa.String(128), nullable=True),
        sa.Column("political_status", sa.String(32), nullable=True),
        sa.Column("phone", sa.String(32), nullable=True),
        sa.Column("emergency_contact_name", sa.String(64), nullable=True),
        sa.Column("emergency_contact_phone", sa.String(32), nullable=True),
        sa.Column("bank_account", sa.String(64), nullable=True),
        sa.Column("contract_type", sa.String(32), nullable=True),
        sa.Column("transfer_history", sa.String(512), nullable=True),
        sa.Column("offboarding_type", sa.String(32), nullable=True),
        sa.Column("offboarding_reason", sa.String(256), nullable=True),
        sa.Column("reason_2", sa.String(256), nullable=True),
        sa.Column("remarks", sa.JSON(), nullable=True),
        sa.Column("feishu_record_id", sa.String(64), nullable=True),
        sa.Column("feishu_synced_at", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="hr",
    )

    op.create_table(
        "training_ledgers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("employee_number", sa.String(32), nullable=True),
        sa.Column("training_date", sa.Date(), nullable=True),
        sa.Column("training_subject", sa.String(256), nullable=True),
        sa.Column("training_method", sa.String(64), nullable=True),
        sa.Column("duration_hours", sa.Float(), nullable=True),
        sa.Column("location", sa.String(128), nullable=True),
        sa.Column("trainer", sa.String(64), nullable=True),
        sa.Column("assessment_result", sa.String(64), nullable=True),
        sa.Column("source_type", sa.String(16), nullable=True, server_default="manual"),
        sa.Column("source_id", sa.Uuid(), nullable=True),
        sa.Column("remarks", sa.String(512), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="hr",
    )

    op.create_table(
        "training_ledger_pages",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("employee_number", sa.String(32), nullable=False),
        sa.Column("employee_name", sa.String(64), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("employee_number"),
        schema="hr",
    )

    op.create_table(
        "annual_training_plans",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("department", sa.String(64), nullable=True),
        sa.Column("status", sa.String(16), nullable=False, server_default="草稿"),
        sa.PrimaryKeyConstraint("id"),
        schema="hr",
    )

    op.create_table(
        "annual_training_plan_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("plan_id", sa.Uuid(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=True),
        sa.Column("trainee_count", sa.Integer(), nullable=True),
        sa.Column("duration_hours", sa.Float(), nullable=True),
        sa.Column("content_and_textbook", sa.String(512), nullable=True),
        sa.Column("target_audience", sa.String(256), nullable=True),
        sa.Column("position_and_count", sa.String(256), nullable=True),
        sa.Column("training_method", sa.String(64), nullable=True),
        sa.Column("training_hours", sa.Float(), nullable=True),
        sa.Column("confirmer", sa.String(64), nullable=True),
        sa.Column("confirm_date", sa.Date(), nullable=True),
        sa.Column("remarks", sa.String(512), nullable=True),
        sa.Column("tracking_status", sa.String(16), nullable=True, server_default="未完成"),
        sa.Column("sort_order", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["plan_id"], ["hr.annual_training_plans.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        schema="hr",
    )


def downgrade() -> None:
    op.drop_table("annual_training_plan_items", schema="hr")
    op.drop_table("annual_training_plans", schema="hr")
    op.drop_table("training_ledger_pages", schema="hr")
    op.drop_table("training_ledgers", schema="hr")
    op.drop_table("departure_records", schema="hr")
    op.drop_table("onboarding_records", schema="hr")
    op.drop_table("offboarding_records", schema="hr")
    op.drop_table("employees", schema="hr")
    op.drop_table("teams", schema="hr")
    op.drop_table("departments", schema="hr")
    op.execute("DROP SCHEMA IF EXISTS hr")
