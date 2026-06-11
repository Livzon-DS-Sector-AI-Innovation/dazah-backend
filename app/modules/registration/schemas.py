"""Registration request and response schemas live here."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# ── 品种对照表 ──────────────────────────────────────────

class ProductInfo(BaseModel):
    """品种登记号对照表条目"""
    product_name: str = Field(..., description="品种名称")
    registration_number: str = Field(..., description="登记号")


# ── 授权书生成 ──────────────────────────────────────────

class AuthorizationLetterCreate(BaseModel):
    """生成授权书请求"""
    product_name: str = Field(
        ..., max_length=128, description="产品名称（对照表标准名）"
    )
    registration_number: str = Field(..., max_length=32, description="产品登记号")
    preparation_unit: str = Field(..., max_length=256, description="制剂单位名称")
    preparation_name: str = Field(..., max_length=256, description="制剂名称")
    administration_route: str = Field(..., max_length=64, description="给药途径")
    remarks: str | None = Field(None, description="备注")


class AuthorizationLetterResponse(BaseModel):
    """授权书记录响应"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    api_company: str
    product_name: str
    registration_number: str
    preparation_unit: str
    preparation_name: str
    administration_route: str
    template_file_name: str | None = None
    output_file_name: str
    remarks: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AuthorizationLetterListItem(BaseModel):
    """授权书列表项"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_name: str
    registration_number: str
    preparation_unit: str
    preparation_name: str
    administration_route: str
    output_file_name: str
    created_at: datetime | None = None
