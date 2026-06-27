"""研发项目管理 Pydantic schemas"""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ===== Project Schemas =====

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
