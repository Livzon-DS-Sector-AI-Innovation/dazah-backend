"""Administration request and response schemas live here."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


# ─── Vehicle Schemas ───

class VehicleCreate(BaseModel):
    plate_number: str = Field(..., max_length=32, description="车牌号")
    brand: str | None = Field(None, max_length=64, description="品牌")
    model: str | None = Field(None, max_length=64, description="型号")
    color: str | None = Field(None, max_length=32, description="颜色")
    purchase_date: date | None = Field(None, description="购买日期")
    mileage: int | None = Field(None, description="行驶里程")
    status: str = Field("可用", max_length=16, description="状态: 可用, 维修中, 已报废")
    owner_department: str | None = Field(None, max_length=64, description="所属部门")
    remarks: str | None = Field(None, description="备注")


class VehicleUpdate(BaseModel):
    plate_number: str | None = Field(None, max_length=32, description="车牌号")
    brand: str | None = Field(None, max_length=64, description="品牌")
    model: str | None = Field(None, max_length=64, description="型号")
    color: str | None = Field(None, max_length=32, description="颜色")
    purchase_date: date | None = Field(None, description="购买日期")
    mileage: int | None = Field(None, description="行驶里程")
    status: str | None = Field(None, max_length=16, description="状态: 可用, 维修中, 已报废")
    owner_department: str | None = Field(None, max_length=64, description="所属部门")
    remarks: str | None = Field(None, description="备注")


class VehicleResponse(BaseModel):
    id: UUID
    plate_number: str
    brand: str | None
    model: str | None
    color: str | None
    purchase_date: date | None
    mileage: int | None
    status: str
    owner_department: str | None
    feishu_record_id: str | None
    feishu_synced_at: datetime | None
    remarks: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── Vehicle Request Schemas ───

class VehicleRequestCreate(BaseModel):
    applicant_name: str = Field(..., max_length=64, description="申请人姓名")
    applicant_department: str | None = Field(None, max_length=64, description="申请人部门")
    applicant_phone: str | None = Field(None, max_length=32, description="联系电话")
    purpose: str = Field(..., description="用车事由")
    destination: str | None = Field(None, max_length=256, description="目的地")
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")
    passengers: int = Field(1, description="乘车人数")
    remarks: str | None = Field(None, description="备注")


class VehicleRequestUpdate(BaseModel):
    applicant_name: str | None = Field(None, max_length=64, description="申请人姓名")
    applicant_department: str | None = Field(None, max_length=64, description="申请人部门")
    applicant_phone: str | None = Field(None, max_length=32, description="联系电话")
    vehicle_id: UUID | None = Field(None, description="分配车辆ID")
    purpose: str | None = Field(None, description="用车事由")
    destination: str | None = Field(None, max_length=256, description="目的地")
    start_time: datetime | None = Field(None, description="开始时间")
    end_time: datetime | None = Field(None, description="结束时间")
    passengers: int | None = Field(None, description="乘车人数")
    status: str | None = Field(None, max_length=16, description="状态: 待审批, 已通过, 已拒绝, 已完成")
    approver: str | None = Field(None, max_length=64, description="审批人")
    remarks: str | None = Field(None, description="备注")


class VehicleRequestResponse(BaseModel):
    id: UUID
    applicant_name: str
    applicant_department: str | None
    applicant_phone: str | None
    vehicle_id: UUID | None
    purpose: str
    destination: str | None
    start_time: datetime
    end_time: datetime
    passengers: int | None
    status: str
    approver: str | None
    approved_at: datetime | None
    remarks: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── IT Service Ticket Schemas ───

class ITServiceTicketCreate(BaseModel):
    ticket_no: str = Field(..., max_length=32, description="工单编号")
    requester_name: str = Field(..., max_length=64, description="报障人姓名")
    requester_department: str | None = Field(None, max_length=64, description="报障人部门")
    requester_phone: str | None = Field(None, max_length=32, description="联系电话")
    ticket_type: str = Field(..., max_length=32, description="工单类型: 硬件故障, 软件问题, 网络问题, 账号权限, 其他")
    priority: str = Field("中", max_length=16, description="优先级: 低, 中, 高, 紧急")
    title: str = Field(..., max_length=128, description="问题标题")
    description: str | None = Field(None, description="问题描述")
    remarks: str | None = Field(None, description="备注")


class ITServiceTicketUpdate(BaseModel):
    ticket_no: str | None = Field(None, max_length=32, description="工单编号")
    requester_name: str | None = Field(None, max_length=64, description="报障人姓名")
    requester_department: str | None = Field(None, max_length=64, description="报障人部门")
    requester_phone: str | None = Field(None, max_length=32, description="联系电话")
    ticket_type: str | None = Field(None, max_length=32, description="工单类型")
    priority: str | None = Field(None, max_length=16, description="优先级")
    title: str | None = Field(None, max_length=128, description="问题标题")
    description: str | None = Field(None, description="问题描述")
    status: str | None = Field(None, max_length=16, description="状态: 待处理, 处理中, 已解决, 已关闭")
    assigned_to: str | None = Field(None, max_length=64, description="指派给")
    resolved_at: datetime | None = Field(None, description="解决时间")
    solution: str | None = Field(None, description="解决方案")
    remarks: str | None = Field(None, description="备注")


class ITServiceTicketResponse(BaseModel):
    id: UUID
    ticket_no: str
    requester_name: str
    requester_department: str | None
    requester_phone: str | None
    ticket_type: str
    priority: str
    title: str
    description: str | None
    status: str
    assigned_to: str | None
    resolved_at: datetime | None
    solution: str | None
    feishu_record_id: str | None
    feishu_synced_at: datetime | None
    remarks: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
