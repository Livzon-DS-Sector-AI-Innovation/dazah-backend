"""Authorization letter and supplementary reply schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProductInfo(BaseModel):
    """品种登记号对照表条目"""
    product_name: str = Field(..., description="品种名称")
    registration_number: str = Field(..., description="登记号")


class AuthorizationLetterCreate(BaseModel):
    """生成授权书请求"""
    product_name: str = Field(..., max_length=128, description="产品名称（对照表标准名）")
    registration_number: str = Field(..., max_length=32, description="产品登记号")
    preparation_unit: str = Field(..., max_length=256, description="制剂单位名称")
    preparation_name: str = Field(..., max_length=256, description="制剂名称")
    administration_route: str = Field(..., max_length=64, description="给药途径")
    remarks: str | None = Field(None, description="备注")


class AuthorizationLetterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_name: str
    registration_number: str
    preparation_unit: str
    preparation_name: str
    administration_route: str
    remarks: str | None = None
    output_file_name: str | None = None
    created_at: datetime
    updated_at: datetime


class AuthorizationLetterListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_name: str
    registration_number: str
    preparation_unit: str
    preparation_name: str
    administration_route: str
    output_file_name: str | None = None
    created_at: datetime
    updated_at: datetime


class SupplementaryReplyCreate(BaseModel):
    """生成发补回复请求"""
    drug_name: str | None = Field(None, max_length=128, description="药品名称")
    registration_number: str | None = Field(None, max_length=64, description="登记号")
    acceptance_number: str | None = Field(None, max_length=64, description="受理号")
    company_name: str | None = Field(None, max_length=256, description="申请人/公司名称")
    remarks: str | None = Field(None, description="备注")


class SupplementaryReplyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    drug_name: str | None = None
    registration_number: str | None = None
    acceptance_number: str | None = None
    company_name: str | None = None
    remarks: str | None = None
    output_file_name: str | None = None
    created_at: datetime
    updated_at: datetime


class SupplementaryReplyListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    drug_name: str | None = None
    registration_number: str | None = None
    acceptance_number: str | None = None
    company_name: str | None = None
    output_file_name: str | None = None
    created_at: datetime
    updated_at: datetime
