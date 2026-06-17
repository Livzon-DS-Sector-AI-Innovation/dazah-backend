"""Research ORM models."""

import uuid
from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, Float, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import BaseModel


class ResearchProject(BaseModel):
    """研发项目主表"""

    __tablename__ = "research_projects"
    __table_args__ = (
        CheckConstraint(
            "stage IN ('立项', '研发中试', '验证', '注册', '商业化')",
            name="ck_research_projects_stage",
        ),
        CheckConstraint(
            "status IN ('进行中', '已暂停', '已完成', '已终止')",
            name="ck_research_projects_status",
        ),
        {"schema": "research"},
    )

    project_no: Mapped[str] = mapped_column(
        String(50), comment="项目编号"
    )
    name: Mapped[str] = mapped_column(
        String(200), comment="项目名称"
    )
    project_type: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="项目类型"
    )
    stage: Mapped[str] = mapped_column(
        String(20),
        default="立项",
        comment="项目阶段：立项/研发中试/验证/注册/商业化",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="进行中",
        comment="项目状态：进行中/已暂停/已完成/已终止",
    )
    leader: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="项目负责人"
    )
    start_date: Mapped[date | None] = mapped_column(
        Date, nullable=True, comment="开始日期"
    )
    end_date: Mapped[date | None] = mapped_column(
        Date, nullable=True, comment="结束日期"
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="项目描述"
    )


class ICHAnalysisRecord(BaseModel):
    """ICH Q3C/Q3D 杂质识别分析记录"""

    __tablename__ = "ich_analysis_records"
    __table_args__ = {"schema": "research"}

    filename: Mapped[str] = mapped_column(
        String(500), comment="上传的文件名"
    )
    route: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="给药途径: oral/parenteral/inhalation/cutaneous (deprecated)"
    )
    q3c_result: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, comment="Q3C 溶剂残留分析结果"
    )
    q3d_result: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, comment="Q3D 元素杂质分析结果"
    )
    llm_used: Mapped[bool] = mapped_column(
        default=False, comment="是否使用 LLM 增强识别"
    )
    notes: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="备注"
    )


class PilotWorkflow(BaseModel):
    """中试研究实例"""

    __tablename__ = "pilot_workflows"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'running', 'waiting_approval', 'completed', 'failed')",
            name="ck_pilot_workflows_status",
        ),
        {"schema": "research"},
    )

    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, comment="关联研发项目ID"
    )
    product_name: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="产品名称"
    )
    scale_up_ratio: Mapped[float] = mapped_column(
        Float, nullable=False, comment="放大倍数"
    )
    equipment_type: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="设备类型"
    )
    equipment_volume: Mapped[float] = mapped_column(
        Float, nullable=False, comment="设备容积(L)"
    )
    input_document_path: Mapped[str | None] = mapped_column(
        String(500), nullable=True, comment="上传文档路径"
    )
    input_context: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, comment="额外上下文"
    )
    status: Mapped[str] = mapped_column(
        String(20), default="pending", comment="状态"
    )
    final_report: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, comment="最终报告"
    )


class PilotWorkflowStep(BaseModel):
    """工作流步骤执行记录"""

    __tablename__ = "pilot_workflow_steps"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'running', 'waiting_approval', 'completed', 'failed', 'skipped')",
            name="ck_pilot_workflow_steps_status",
        ),
        {"schema": "research"},
    )

    workflow_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, comment="工作流ID"
    )
    step_order: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="步骤序号"
    )
    step_code: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="步骤标识"
    )
    step_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="步骤名称"
    )
    status: Mapped[str] = mapped_column(
        String(20), default="pending", comment="状态"
    )
    input_data: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, comment="输入数据"
    )
    output_data: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, comment="输出数据"
    )
    error_message: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="错误信息"
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="开始时间"
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="完成时间"
    )
