"""Work order schemas."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

# ==================== 维修工单 ====================
WorkOrderType = Literal["故障维修", "校准"]
WorkOrderPriority = Literal["紧急", "高", "中", "低"]
WorkOrderStatus = Literal["待处理", "已指派", "维修中", "待验收", "已完成", "已关闭"]
VerificationResult = Literal["合格", "不合格"]


class WorkOrderCreate(BaseModel):
    """创建工单请求"""

    equipment_id: uuid.UUID = Field(..., description="设备ID")
    order_type: WorkOrderType = Field(default="故障维修", description="工单类型")
    priority: WorkOrderPriority = Field(default="中", description="优先级")
    fault_symptom_id: uuid.UUID | None = Field(default=None, description="故障现象ID")
    fault_cause_id: uuid.UUID | None = Field(default=None, description="故障原因ID")
    fault_action_id: uuid.UUID | None = Field(default=None, description="维修措施ID")
    fault_description: str | None = Field(default=None, description="故障详细描述")


class WorkOrderAssign(BaseModel):
    """指派工单请求"""

    assignee_id: uuid.UUID = Field(..., description="维修人ID")


class WorkOrderComplete(BaseModel):
    """完成工单请求"""

    repair_detail: str = Field(..., min_length=1, description="维修过程描述")


class WorkOrderVerify(BaseModel):
    """验收工单请求"""

    result: VerificationResult = Field(..., description="验收结果")
    remark: str | None = Field(default=None, description="验收备注")


class WorkOrderResponse(BaseModel):
    """工单响应"""

    id: uuid.UUID
    work_order_no: str
    equipment_id: uuid.UUID
    order_type: WorkOrderType
    priority: WorkOrderPriority
    status: WorkOrderStatus
    fault_symptom_id: uuid.UUID | None
    fault_cause_id: uuid.UUID | None
    fault_action_id: uuid.UUID | None
    fault_description: str | None
    reporter_id: uuid.UUID
    assignee_id: uuid.UUID | None
    verified_by: uuid.UUID | None
    reported_at: datetime
    assigned_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
    verified_at: datetime | None
    verification_result: VerificationResult | None
    verification_remark: str | None
    repair_detail: str | None
    actual_duration: int | None
    original_equipment_status: str | None
    created_at: datetime
    updated_at: datetime
    created_by: uuid.UUID | None
    updated_by: uuid.UUID | None

    model_config = {"from_attributes": True}


class WorkOrderStatistics(BaseModel):
    """工单统计"""

    total: int
    by_status: dict[str, int]
    by_type: dict[str, int]
    by_priority: dict[str, int]
