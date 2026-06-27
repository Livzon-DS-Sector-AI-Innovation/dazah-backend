"""Research request and response schemas."""

import uuid
from uuid import UUID
from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

ResearchProjectStage = Literal["立项", "研发中试", "验证", "注册", "商业化"]
ResearchProjectStatus = Literal["进行中", "已暂停", "已完成", "已终止"]


class ResearchProjectCreate(BaseModel):
    """创建研发项目请求"""

    project_no: str | None = Field(default=None, max_length=50, description="项目编号（可选，不填则自动生成）")
    name: str = Field(..., min_length=1, max_length=200, description="项目名称")
    project_type: str | None = Field(default=None, max_length=100, description="项目类型")
    stage: ResearchProjectStage = Field(default="立项", description="项目阶段")
    status: ResearchProjectStatus = Field(default="进行中", description="项目状态")
    leader: str | None = Field(default=None, max_length=100, description="项目负责人")
    start_date: date | None = Field(default=None, description="开始日期")
    end_date: date | None = Field(default=None, description="结束日期")
    description: str | None = Field(default=None, description="项目描述")


class ResearchProjectUpdate(BaseModel):
    """更新研发项目请求"""

    project_no: str | None = Field(default=None, min_length=1, max_length=50)
    name: str | None = Field(default=None, min_length=1, max_length=200)
    project_type: str | None = Field(default=None, max_length=100)
    stage: ResearchProjectStage | None = None
    status: ResearchProjectStatus | None = None
    leader: str | None = Field(default=None, max_length=100)
    start_date: date | None = None
    end_date: date | None = None
    description: str | None = None


class ResearchProjectResponse(BaseModel):
    """研发项目响应"""

    id: uuid.UUID
    project_no: str
    name: str
    project_type: str | None
    stage: str
    status: str
    leader: str | None
    start_date: date | None
    end_date: date | None
    description: str | None
    created_at: datetime
    updated_at: datetime
    created_by: uuid.UUID | None
    updated_by: uuid.UUID | None

    model_config = {"from_attributes": True}


class EDBOOptimizeRequest(BaseModel):
    """EDBO+ 贝叶斯优化请求"""

    objectives: list[str] = Field(..., min_length=1, description="目标列名列表")
    objective_modes: list[Literal["max", "min"]] = Field(
        ..., min_length=1, description="目标方向（max/min），与 objectives 一一对应"
    )
    batch_size: int = Field(default=5, ge=1, le=100, description="建议实验数量")


class EDBOOptimizeResponse(BaseModel):
    """EDBO+ 贝叶斯优化响应"""

    csv_data: str = Field(..., description="结果 CSV 文本")
    row_count: int = Field(..., description="结果行数")
    prediction_data: Optional[str] = Field(None, description="预测文件 CSV 文本（可选）")
    prediction_filename: Optional[str] = Field(None, description="预测文件名（可选）")


# ===== Pilot Workflow Schemas =====

PilotWorkflowStatus = Literal["pending", "running", "waiting_approval", "completed", "failed"]
PilotWorkflowStepStatus = Literal[
    "pending", "running", "waiting_approval", "completed", "failed", "skipped"
]


class PilotWorkflowCreate(BaseModel):
    """创建中试研究"""

    project_id: uuid.UUID | None = Field(default=None, description="关联研发项目ID")
    product_name: str = Field(..., min_length=1, max_length=200, description="产品名称")
    scale_up_ratio: float = Field(..., gt=0, description="放大倍数")
    equipment_type: str = Field(
        ..., min_length=1, max_length=100, description="设备类型"
    )
    equipment_volume: float = Field(..., gt=0, description="设备容积(L)")
    input_context: dict | None = Field(default=None, description="额外上下文信息")


class PilotWorkflowStepResponse(BaseModel):
    """工作流步骤响应"""

    id: uuid.UUID
    workflow_id: uuid.UUID
    step_order: int
    step_code: str
    step_name: str
    status: str
    input_data: dict | None
    output_data: dict | None
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PilotWorkflowResponse(BaseModel):
    """工作流响应"""

    id: uuid.UUID
    project_id: uuid.UUID | None
    product_name: str
    scale_up_ratio: float
    equipment_type: str
    equipment_volume: float
    input_document_path: str | None
    input_context: dict | None
    status: str
    final_report: dict | None
    created_at: datetime
    updated_at: datetime
    created_by: uuid.UUID | None
    updated_by: uuid.UUID | None
    steps: list[PilotWorkflowStepResponse] = []

    model_config = {"from_attributes": True}


class PilotWorkflowListResponse(BaseModel):
    """工作流列表响应"""

    id: uuid.UUID
    product_name: str
    scale_up_ratio: float
    equipment_type: str
    equipment_volume: float
    status: str
    created_at: datetime
    step_count: int = 0
    completed_step_count: int = 0

    model_config = {"from_attributes": True}


# Alias for backward compatibility
PilotWorkflowListItem = PilotWorkflowListResponse


# ===== Rd Project Schemas (from rd_project) =====

class RdProjectBase(BaseModel):
    name: str = Field(..., max_length=200, description="品种名称")
    api_name: str = Field(..., max_length=200, description="API全称")
    cas_number: Optional[str] = Field(None, max_length=50, description="CAS号")
    molecular_formula: Optional[str] = Field(None, max_length=200, description="分子式")
    molecular_weight: Optional[float] = Field(None, description="分子量")
    indication: Optional[str] = Field(None, max_length=500, description="适应症")
    project_type: Optional[str] = Field(None, max_length=50, description="generic/improved")
    priority: str = Field("normal", max_length=20, description="low/normal/high/urgent")
    project_manager_id: Optional[UUID] = Field(None, description="项目经理ID")
    start_date: Optional[date] = Field(None, description="开始日期")
    target_filing_date: Optional[date] = Field(None, description="目标申报日期")
    notes: Optional[str] = Field(None, description="备注")


class RdProjectCreate(RdProjectBase):
    pass


class RdProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    api_name: Optional[str] = Field(None, max_length=200)
    cas_number: Optional[str] = Field(None, max_length=50)
    molecular_formula: Optional[str] = Field(None, max_length=200)
    molecular_weight: Optional[float] = None
    indication: Optional[str] = Field(None, max_length=500)
    project_type: Optional[str] = Field(None, max_length=50)
    priority: Optional[str] = Field(None, max_length=20)
    project_manager_id: Optional[UUID] = None
    start_date: Optional[date] = None
    target_filing_date: Optional[date] = None
    actual_filing_date: Optional[date] = None
    current_stage: Optional[str] = Field(None, max_length=50)
    overall_progress: Optional[float] = None
    notes: Optional[str] = None


class RdProjectResponse(RdProjectBase):
    id: UUID
    status: str
    current_stage: Optional[str]
    overall_progress: Optional[float]
    actual_filing_date: Optional[date]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]

    model_config = {"from_attributes": True}


# ===== Milestone Schemas =====

class RdMilestoneBase(BaseModel):
    title: str = Field(..., max_length=200, description="标题")
    milestone_type: Optional[str] = Field(None, max_length=50, description="gate_review/decision/achievement")
    stage: Optional[str] = Field(None, max_length=50, description="关联阶段")
    planned_date: Optional[date] = Field(None, description="计划日期")
    decision: Optional[str] = Field(None, max_length=50, description="go/no_go/hold/conditional")
    decision_rationale: Optional[str] = Field(None, description="决策理由")


class RdMilestoneCreate(RdMilestoneBase):
    pass


class RdMilestoneUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    milestone_type: Optional[str] = Field(None, max_length=50)
    stage: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, max_length=50)
    planned_date: Optional[date] = None
    actual_date: Optional[date] = None
    decision: Optional[str] = Field(None, max_length=50)
    decision_rationale: Optional[str] = None


class RdMilestoneResponse(RdMilestoneBase):
    id: UUID
    project_id: UUID
    status: str
    actual_date: Optional[date]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ===== Stage Record Schemas =====

class RdStageRecordBase(BaseModel):
    stage: str = Field(..., max_length=50, description="initiation/route_dev/optimization/pilot/validation/filing")
    version: int = Field(1, description="版本号")
    input_summary: Optional[dict] = Field(None, description="上游输入摘要")
    input_references: Optional[dict] = Field(None, description="关联的上游记录ID")
    output_summary: Optional[dict] = Field(None, description="产出摘要")
    deliverables: Optional[dict] = Field(None, description="产出物列表")


class RdStageRecordCreate(RdStageRecordBase):
    pass


class RdStageRecordUpdate(BaseModel):
    status: Optional[str] = Field(None, max_length=50)
    input_summary: Optional[dict] = None
    input_references: Optional[dict] = None
    output_summary: Optional[dict] = None
    deliverables: Optional[dict] = None
    gate_review_status: Optional[str] = Field(None, max_length=50)
    gate_hard_conditions: Optional[dict] = None
    gate_soft_conditions: Optional[dict] = None
    gate_review_notes: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class RdStageRecordResponse(RdStageRecordBase):
    id: UUID
    project_id: UUID
    status: str
    gate_review_status: Optional[str]
    gate_reviewed_at: Optional[datetime]
    gate_reviewed_by: Optional[UUID]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ===== Research Track Schemas =====

class RdResearchTrackBase(BaseModel):
    type: str = Field(..., max_length=50, description="impurity/crystal_form/stability/quality_standard/custom")
    name: str = Field(..., max_length=200, description="研究项名称")
    description: Optional[str] = Field(None, description="描述")
    priority: str = Field("normal", max_length=20, description="low/normal/high/urgent")
    owner_id: Optional[UUID] = Field(None, description="负责人ID")


class RdResearchTrackCreate(RdResearchTrackBase):
    pass


class RdResearchTrackUpdate(BaseModel):
    type: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    status: Optional[str] = Field(None, max_length=50)
    priority: Optional[str] = Field(None, max_length=20)
    current_conclusion: Optional[str] = None
    conclusion_version: Optional[int] = None
    conclusion_confidence: Optional[str] = Field(None, max_length=50)
    active_stages: Optional[list[str]] = None
    owner_id: Optional[UUID] = None


class RdResearchTrackResponse(RdResearchTrackBase):
    id: UUID
    project_id: UUID
    status: str
    current_conclusion: Optional[str]
    conclusion_version: int
    conclusion_confidence: Optional[str]
    active_stages: Optional[list[str]]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ===== Research Finding Schemas =====

class RdResearchFindingBase(BaseModel):
    finding_type: Optional[str] = Field(None, max_length=50, description="identification/classification/control_strategy/characterization")
    data: dict = Field(..., description="结构化数据")
    conclusion: Optional[str] = Field(None, description="结论")
    confidence: str = Field("preliminary", max_length=50, description="preliminary/confirmed/final")
    attachments: Optional[dict] = Field(None, description="附件列表")


class RdResearchFindingCreate(RdResearchFindingBase):
    stage_record_id: Optional[UUID] = Field(None, description="关联阶段记录ID")


class RdResearchFindingUpdate(BaseModel):
    finding_type: Optional[str] = Field(None, max_length=50)
    data: Optional[dict] = None
    conclusion: Optional[str] = None
    confidence: Optional[str] = Field(None, max_length=50)
    attachments: Optional[dict] = None
    version: Optional[int] = None


class RdResearchFindingResponse(RdResearchFindingBase):
    id: UUID
    track_id: UUID
    stage_record_id: Optional[UUID]
    version: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]

    model_config = {"from_attributes": True}


# Rebuild models to resolve forward references
RdProjectResponse.model_rebuild()
RdMilestoneResponse.model_rebuild()
RdStageRecordResponse.model_rebuild()
RdResearchTrackResponse.model_rebuild()
RdResearchFindingResponse.model_rebuild()
