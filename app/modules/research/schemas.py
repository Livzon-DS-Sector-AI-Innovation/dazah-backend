"""Research schemas for Bayesian optimization."""

import uuid
from datetime import datetime
from pydantic import BaseModel, Field


# ============ Component Schemas ============
class ComponentBase(BaseModel):
    name: str = Field(..., description="组件名称")
    lower_bound: float = Field(..., description="下限")
    upper_bound: float = Field(..., description="上限")
    interval: float | None = Field(None, description="间隔")
    unit: str | None = Field(None, description="单位")
    sort_order: int = Field(0, description="排序")


class ComponentCreate(ComponentBase):
    pass


class ComponentResponse(ComponentBase):
    id: uuid.UUID
    project_id: uuid.UUID
    created_at: datetime


# ============ Objective Schemas ============
class ObjectiveBase(BaseModel):
    name: str = Field(..., description="目标名称")
    direction: str = Field("maximize", description="优化方向: maximize/minimize")
    weight: float = Field(1.0, description="权重")


class ObjectiveCreate(ObjectiveBase):
    pass


class ObjectiveResponse(ObjectiveBase):
    id: uuid.UUID
    project_id: uuid.UUID
    created_at: datetime


# ============ Project Schemas ============
class ProjectBase(BaseModel):
    name: str = Field(..., description="项目名称")
    description: str | None = Field(None, description="项目描述")


class ProjectCreate(ProjectBase):
    components: list[ComponentCreate] = Field(default=[], description="组件列表")
    objectives: list[ObjectiveCreate] = Field(default=[], description="目标列表")


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None


class ProjectResponse(ProjectBase):
    id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime


class ProjectDetail(ProjectResponse):
    components: list[ComponentResponse] = []
    objectives: list[ObjectiveResponse] = []


# ============ Experiment Schemas ============
class ExperimentBase(BaseModel):
    batch_number: int = Field(..., description="批次号")
    parameters: dict = Field(..., description="参数组合")
    results: dict | None = Field(None, description="实验结果")
    is_suggested: bool = Field(True, description="是否推荐")
    status: str = Field("pending", description="状态")


class ExperimentCreate(ExperimentBase):
    project_id: uuid.UUID


class ExperimentResponse(ExperimentBase):
    id: uuid.UUID
    project_id: uuid.UUID
    created_at: datetime


class ExperimentSuggest(BaseModel):
    """请求推荐下一批实验"""
    project_id: uuid.UUID
    num_experiments: int = Field(5, ge=1, le=20, description="推荐实验数量")


# ============ Reaction Scope Schemas ============
class ReactionScopeCreate(BaseModel):
    project_id: uuid.UUID
    name: str = Field(..., description="范围名称")


class ReactionScopeResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    scope_data: dict
    total_combinations: int
    created_at: datetime


# ============ CSV Import Schemas ============
class CSVImportResponse(BaseModel):
    success: bool
    message: str
    rows_imported: int = 0
    preview: list[dict] = Field(default=[], description="预览数据")
