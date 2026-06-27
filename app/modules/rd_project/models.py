"""研发项目管理 ORM 模型"""

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, Integer, JSON, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import BaseModel


class RdProject(BaseModel):
    """研发项目主表"""
    __tablename__ = "rd_projects"
    __table_args__ = {"schema": "research"}

    name: Mapped[str] = mapped_column(String(200), comment="品种名称")
    api_name: Mapped[str] = mapped_column(String(200), comment="API全称")
    cas_number: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="CAS号")
    molecular_formula: Mapped[str | None] = mapped_column(String(200), nullable=True, comment="分子式")
    molecular_weight: Mapped[float | None] = mapped_column(Float, nullable=True, comment="分子量")
    indication: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="适应症")
    project_type: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="generic/improved")
    status: Mapped[str] = mapped_column(String(50), default="initiation", comment="当前阶段状态")
    priority: Mapped[str] = mapped_column(String(20), default="normal", comment="low/normal/high/urgent")
    
    project_manager_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("identity.users.id"), nullable=True, comment="项目经理"
    )
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment="开始日期")
    target_filing_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment="目标申报日期")
    actual_filing_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment="实际申报日期")
    
    current_stage: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="当前阶段")
    overall_progress: Mapped[float | None] = mapped_column(Float, nullable=True, comment="总体进度%")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")


class RdMilestone(BaseModel):
    """里程碑/决策记录"""
    __tablename__ = "rd_milestones"
    __table_args__ = {"schema": "research"}

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("research.rd_projects.id"), comment="项目ID"
    )
    title: Mapped[str] = mapped_column(String(200), comment="标题")
    milestone_type: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="gate_review/decision/achievement")
    stage: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="关联阶段")
    status: Mapped[str] = mapped_column(String(50), default="planned", comment="planned/achieved/delayed/cancelled")
    planned_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment="计划日期")
    actual_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment="实际日期")
    decision: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="go/no_go/hold/conditional")
    decision_rationale: Mapped[str | None] = mapped_column(Text, nullable=True, comment="决策理由")


class RdStageRecord(BaseModel):
    """阶段记录"""
    __tablename__ = "rd_stage_records"
    __table_args__ = {"schema": "research"}

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("research.rd_projects.id"), comment="项目ID"
    )
    stage: Mapped[str] = mapped_column(String(50), comment="initiation/route_dev/optimization/pilot/validation/filing")
    status: Mapped[str] = mapped_column(String(50), default="not_started", comment="not_started/in_progress/review/completed/transferred")
    version: Mapped[int] = mapped_column(Integer, default=1, comment="版本号")
    
    input_summary: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment="上游输入摘要")
    input_references: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment="关联的上游记录ID")
    output_summary: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment="产出摘要")
    deliverables: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment="产出物列表")
    
    gate_review_status: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="pending/approved/rejected/conditional")
    gate_hard_conditions: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment="硬条件检查结果")
    gate_soft_conditions: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment="软条件检查结果")
    gate_review_notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="评审备注")
    gate_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    gate_reviewed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("identity.users.id"), nullable=True
    )
    
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class RdResearchTrack(BaseModel):
    """研究项（跨阶段并行）"""
    __tablename__ = "rd_research_tracks"
    __table_args__ = {"schema": "research"}

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("research.rd_projects.id"), comment="项目ID"
    )
    type: Mapped[str] = mapped_column(String(50), comment="impurity/crystal_form/stability/quality_standard/custom")
    name: Mapped[str] = mapped_column(String(200), comment="研究项名称")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="描述")
    status: Mapped[str] = mapped_column(String(50), default="active", comment="active/paused/completed/archived")
    priority: Mapped[str] = mapped_column(String(20), default="normal", comment="low/normal/high/urgent")
    
    current_conclusion: Mapped[str | None] = mapped_column(Text, nullable=True, comment="当前结论")
    conclusion_version: Mapped[int] = mapped_column(Integer, default=0, comment="结论版本号")
    conclusion_confidence: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="preliminary/confirmed/final")
    
    active_stages: Mapped[list | None] = mapped_column(ARRAY(String(50)), nullable=True, comment="活跃阶段列表")
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("identity.users.id"), nullable=True, comment="负责人"
    )


class RdResearchFinding(BaseModel):
    """研究发现"""
    __tablename__ = "rd_research_findings"
    __table_args__ = {"schema": "research"}

    track_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("research.rd_research_tracks.id"), comment="研究项ID"
    )
    stage_record_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("research.rd_stage_records.id"), nullable=True, comment="关联阶段记录"
    )
    
    finding_type: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="identification/classification/control_strategy/characterization")
    data: Mapped[dict] = mapped_column(JSON, comment="结构化数据")
    conclusion: Mapped[str | None] = mapped_column(Text, nullable=True, comment="结论")
    confidence: Mapped[str] = mapped_column(String(50), default="preliminary", comment="preliminary/confirmed/final")
    
    attachments: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment="附件列表")
    version: Mapped[int] = mapped_column(Integer, default=1, comment="版本号")
