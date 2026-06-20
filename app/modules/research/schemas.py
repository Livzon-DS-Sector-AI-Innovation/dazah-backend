"""Research request and response schemas."""

import uuid
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
PilotWorkflowStepStatus = Literal["pending", "running", "waiting_approval", "completed", "failed", "skipped"]


class PilotWorkflowStepResponse(BaseModel):
    """工作流步骤响应"""
    id: str
    workflow_id: str
    step_order: int
    step_code: str
    step_name: str
    status: str
    input_data: dict | None = None
    output_data: dict | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PilotWorkflowCreate(BaseModel):
    """创建中试工作流请求"""
    project_id: str | None = Field(default=None, max_length=50, description="所属研发项目ID")
    product_name: str = Field(..., min_length=1, max_length=200, description="产品名称")
    scale_up_ratio: float = Field(default=10.0, ge=1, le=10000, description="放大倍数")
    equipment_type: str = Field(..., min_length=1, max_length=100, description="设备类型")
    equipment_volume: float = Field(..., ge=1, le=100000, description="设备容积(L)")
    input_context: dict | None = Field(default=None, description="输入上下文")


class PilotWorkflowResponse(BaseModel):
    """中试工作流响应"""
    id: str
    project_id: str | None
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


class PilotWorkflowListItem(BaseModel):
    """中试工作流列表项"""
    id: str
    product_name: str
    scale_up_ratio: float
    equipment_type: str
    equipment_volume: float
    status: str
    created_at: datetime
    step_count: int = 0
    completed_step_count: int = 0

    model_config = {"from_attributes": True}
