"""Procurement request and response schemas live here."""

from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class InvoiceLineItem(BaseModel):
    project_name: str | None = Field(None, description="项目名称")
    unit: str | None = Field(None, description="单位")
    quantity: Decimal | None = Field(None, description="数量")


class InvoiceRecognitionResult(BaseModel):
    invoice_number: str | None = Field(None, description="发票号码")
    invoice_date: str | None = Field(None, description="开票日期")
    seller_name: str | None = Field(None, description="销售方名称")
    total_tax_amount: Decimal | None = Field(None, description="税额合计")
    total_amount_with_tax_small: Decimal | None = Field(
        None,
        description="价税合计（小写）",
    )
    line_items: list[InvoiceLineItem] = Field(
        default_factory=list,
        description="发票明细",
    )
    raw_text: str = Field("", description="PDF 文本层原文")


class InvoiceRecognitionRecordResponse(InvoiceRecognitionResult):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="识别记录 ID")
    file_name: str = Field(..., description="上传文件名")
    include_details: bool = Field(False, description="是否开启明细识别")
    created_at: datetime | None = Field(None, description="识别时间")


class InvoiceRecognitionResponse(BaseModel):
    code: int = Field(200, description="响应状态码")
    message: str = Field("success", description="响应消息")
    data: InvoiceRecognitionRecordResponse
    meta: dict[str, Any] | None = None


class InvoiceRecognitionRecordListResponse(BaseModel):
    code: int = Field(200, description="响应状态码")
    message: str = Field("success", description="响应消息")
    data: list[InvoiceRecognitionRecordResponse]
    meta: dict[str, Any] | None = None


class InvoiceRecognitionRecordDeleteRequest(BaseModel):
    ids: list[UUID] = Field(default_factory=list, description="识别记录 ID 列表")


class InvoiceRecognitionRecordDeleteResult(BaseModel):
    success_count: int = Field(0, description="成功删除数量")
    fail_count: int = Field(0, description="删除失败数量")


class InvoiceRecognitionRecordDeleteResponse(BaseModel):
    code: int = Field(200, description="响应状态码")
    message: str = Field("success", description="响应消息")
    data: InvoiceRecognitionRecordDeleteResult | None = None
    meta: dict[str, Any] | None = None


class PurchaseRequestCategory(StrEnum):
    hardware = "hardware"
    computer = "computer"
    office = "office"
    raw_auxiliary = "raw-auxiliary"
    chemical_glass = "chemical-glass"
    electrical = "electrical"
    labor_protection = "labor-protection"


class PurchaseRequestStatus(StrEnum):
    draft = "draft"
    pending_department_head = "pending_department_head"
    pending_responsible_leader = "pending_responsible_leader"
    approved = "approved"
    rejected = "rejected"


class PurchaseApprovalRole(StrEnum):
    department_head = "department_head"
    responsible_leader = "responsible_leader"


class PurchaseApprovalResult(StrEnum):
    approved = "approved"
    rejected = "rejected"


class PurchaseApprovalView(StrEnum):
    pending = "pending"
    completed = "completed"
    rejected = "rejected"


class PurchaseRequestItemInput(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=255, description="商品名称")
    specification: str = Field("", max_length=255, description="规格")
    purpose: str = Field("", max_length=255, description="用途")
    material: str = Field("", max_length=255, description="材质")
    brand: str = Field("", max_length=255, description="品牌")
    quantity: Decimal = Field(..., ge=0, description="数量")
    unit: str = Field("", max_length=64, description="单位")
    unit_price: Decimal = Field(..., ge=0, description="单价（元）")
    remarks: str = Field("", description="备注")


class PurchaseRequestItemResponse(PurchaseRequestItemInput):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="明细 ID")
    sequence: int = Field(..., description="序号")
    total_amount: Decimal = Field(..., description="总额（元）")


class PurchaseApprovalRequest(BaseModel):
    approval_role: PurchaseApprovalRole = Field(..., description="审批角色")
    approver_name: str = Field("", max_length=100, description="审批人姓名")
    opinion: str = Field("", description="审批意见")
    result: PurchaseApprovalResult = Field(..., description="审批结果")


class PurchaseRequestCreate(BaseModel):
    category: PurchaseRequestCategory = Field(..., description="采购分类")
    request_department: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="申购部门",
    )
    request_date: date = Field(..., description="申请日期")
    items: list[PurchaseRequestItemInput] = Field(
        ...,
        min_length=1,
        description="申请明细",
    )


class PurchaseRequestUpdate(BaseModel):
    request_department: str | None = Field(
        None,
        min_length=1,
        max_length=200,
        description="申购部门",
    )
    request_date: date | None = Field(None, description="申请日期")
    items: list[PurchaseRequestItemInput] | None = Field(
        None,
        min_length=1,
        description="申请明细",
    )


class PurchaseApprovalRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="审批记录 ID")
    approval_role: PurchaseApprovalRole = Field(..., description="审批角色")
    result: PurchaseApprovalResult = Field(..., description="审批结果")
    opinion: str = Field("", description="审批意见")
    approver_name: str = Field("", description="审批人姓名")
    approval_time: datetime = Field(..., description="审批时间")


class PurchaseRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="采购申请 ID")
    category: PurchaseRequestCategory = Field(..., description="采购分类")
    request_department: str = Field(..., description="申购部门")
    request_date: date = Field(..., description="申请日期")
    status: PurchaseRequestStatus = Field(..., description="流程状态")
    total_amount: Decimal = Field(..., description="合计金额")
    rejected_step: PurchaseApprovalRole | None = Field(None, description="驳回步骤")
    status_updated_at: datetime | None = Field(None, description="状态更新时间")
    created_at: datetime | None = Field(None, description="创建时间")
    updated_at: datetime | None = Field(None, description="更新时间")
    items: list[PurchaseRequestItemResponse] = Field(
        default_factory=list,
        description="申请明细",
    )
    approvals: list[PurchaseApprovalRecordResponse] = Field(
        default_factory=list,
        description="审批记录",
    )


class PurchaseRequestApiResponse(BaseModel):
    code: int = Field(200, description="响应状态码")
    message: str = Field("success", description="响应消息")
    data: PurchaseRequestResponse
    meta: dict[str, Any] | None = None


class PurchaseRequestListResponse(BaseModel):
    code: int = Field(200, description="响应状态码")
    message: str = Field("success", description="响应消息")
    data: list[PurchaseRequestResponse]
    meta: dict[str, Any] | None = None


class ContractCategory(StrEnum):
    fixed_assets = "fixed-assets"
    consumables = "consumables"
    hardware = "hardware"
    raw_materials = "raw-materials"


class ContractPartyInfo(BaseModel):
    name: str = Field("", description="单位名称")
    representative: str = Field("", description="法定代表人或签约代表")
    address: str = Field("", description="地址")
    postal_code: str = Field("", description="邮编")
    contact_person: str = Field("", description="联系人")
    contact_address: str = Field("", description="联系人地址")
    contact_phone: str = Field("", description="联系人电话")
    mobile: str = Field("", description="联系人手机")
    phone: str = Field("", description="电话")
    bank_name: str = Field("", description="开户行")
    bank_account: str = Field("", description="银行账号")
    tax_id: str = Field("", description="统一社会信用代码或纳税人识别号")
    bank_line_number: str = Field("", description="银行行号")
    email: str = Field("", description="邮箱")


class ContractItemInput(BaseModel):
    item_code: str = Field("", description="物料或物品编码")
    name: str = Field(..., description="商品或产品名称")
    specification: str = Field("", description="规格")
    quality_standard: str = Field("", description="质量标准或第二规格列")
    manufacturer: str = Field("", description="生产厂家或生产单位")
    department: str = Field("", description="申请部门或备注部门")
    quantity: Decimal = Field(..., gt=0, description="数量")
    unit: str = Field("", description="单位")
    unit_price: Decimal = Field(..., ge=0, description="单价")
    amount: Decimal | None = Field(
        None,
        ge=0,
        description="含税金额，不填则按数量*单价计算",
    )
    remarks: str = Field("", description="备注")


class ContractGenerateRequest(BaseModel):
    category: ContractCategory = Field(..., description="合同分类")
    contract_number: str = Field(..., description="合同编号")
    contract_date: date = Field(..., description="签订日期")
    delivery_date: date | None = Field(None, description="最迟交货日期")
    delivery_terms: str = Field("", description="交货日期或交货说明")
    payment_terms: str = Field("", description="付款期限/付款方式完整描述")
    tax_rate: Decimal = Field(Decimal("13"), ge=0, description="增值税税率")
    seller: ContractPartyInfo = Field(
        default_factory=ContractPartyInfo,
        description="卖方信息",
    )
    items: list[ContractItemInput] = Field(..., min_length=1, description="合同明细")

    buyer_invoice_recipient: str = Field("", description="发票接收人")
    buyer_invoice_recipient_mobile: str = Field("", description="发票接收人手机")
    buyer_receiver: str = Field("", description="收货人")
    buyer_receiver_mobile: str = Field("", description="收货人手机")
    buyer_receiver_phone: str = Field("", description="收货人电话")

    attached_documents: str = Field("", description="固定资产随货资料")
    installation_days: int | None = Field(None, ge=0, description="安装调试工作日")
    warranty_months: int | None = Field(None, ge=0, description="质保期（月）")
    response_hours: int | None = Field(None, ge=0, description="质保期响应小时")
    onsite_hours: int | None = Field(None, ge=0, description="质保期到场处理小时")
    maintenance_response_hours: int | None = Field(
        None,
        ge=0,
        description="质保期满维修响应小时",
    )
    overdue_days: int | None = Field(None, ge=0, description="逾期多少天可解除合同")
    jurisdiction: str = Field("", description="争议管辖地")
    attachment_note: str = Field("", description="附件说明")
    copies: int | None = Field(None, ge=1, description="合同总份数")
    buyer_copies: int | None = Field(None, ge=1, description="买方执份数")
    arrival_payment_condition: str = Field("", description="固定资产到货款支付条件")
    arrival_payment_method: str = Field("", description="固定资产到货款支付方式")
    arrival_payment_ratio: Decimal | None = Field(
        None,
        ge=0,
        le=100,
        description="到货款比例",
    )
    warranty_payment_ratio: Decimal | None = Field(
        None,
        ge=0,
        le=100,
        description="质保金比例",
    )
    warranty_payment_method: str = Field("", description="质保金支付方式")


class ContractTemplateField(BaseModel):
    name: str = Field(..., description="字段名")
    label: str = Field(..., description="显示名称")
    input_type: str = Field("text", description="输入控件类型")
    required: bool = Field(False, description="是否必填")
    default_value: str | None = Field(None, description="默认值")


class ContractTemplateMetadata(BaseModel):
    category: ContractCategory
    label: str
    fields: list[ContractTemplateField]
