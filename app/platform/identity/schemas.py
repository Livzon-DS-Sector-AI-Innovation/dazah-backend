import json
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

UserRole = Literal["admin", "user"]
UserStatus = Literal["active", "disabled"]
AuthSource = Literal["local", "feishu"]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    user: "UserResponse | None" = None


class LocalLoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=1, max_length=255)


class SSOCallbackResult(BaseModel):
    token: str
    redirect_url: str


class UserResponse(BaseModel):
    id: UUID
    name: str
    username: str | None = None
    role: UserRole = "user"
    status: UserStatus = "active"
    auth_source: AuthSource = "feishu"
    en_name: str | None = None
    email: str | None = None
    enterprise_email: str | None = None
    mobile: str | None = None
    avatar_url: str | None = None
    avatar_thumb: str | None = None
    avatar_middle: str | None = None
    avatar_big: str | None = None
    employee_no: str | None = None
    department: str | None = None
    position: str | None = None
    feishu_user_id: str | None = None
    feishu_open_id: str | None = None
    feishu_union_id: str | None = None
    tenant_key: str | None = None

    model_config = {"from_attributes": True}


class UserManagementItem(UserResponse):
    last_login_at: str | None = None

    @field_validator("last_login_at", mode="before")
    @classmethod
    def datetime_to_str(cls, v: object) -> str | None:
        if v is None:
            return None
        if hasattr(v, "isoformat"):
            return v.isoformat()
        return str(v)


class UserManagementListResponse(BaseModel):
    items: list[UserManagementItem]
    total: int
    offset: int
    limit: int


class LocalUserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=64)
    password: str = Field(..., min_length=6, max_length=255)
    name: str = Field(..., min_length=1, max_length=100)
    email: str | None = Field(None, max_length=255)
    mobile: str | None = Field(None, max_length=32)
    employee_no: str | None = Field(None, max_length=64)
    department: str | None = Field(None, max_length=200)
    position: str | None = Field(None, max_length=200)
    role: UserRole = "user"
    status: UserStatus = "active"


class UserManagementUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    email: str | None = Field(None, max_length=255)
    mobile: str | None = Field(None, max_length=32)
    employee_no: str | None = Field(None, max_length=64)
    department: str | None = Field(None, max_length=200)
    position: str | None = Field(None, max_length=200)
    role: UserRole | None = None
    status: UserStatus | None = None


class PasswordResetRequest(BaseModel):
    password: str = Field(..., min_length=6, max_length=255)


# ── Department ──────────────────────────────────────────────────────


class DepartmentResponse(BaseModel):
    id: UUID
    feishu_department_id: str
    name: str
    parent_feishu_department_id: str | None = None
    leader_user_id: str | None = None
    member_count: int | None = None
    status_is_deleted: bool | None = None
    path: str | None = None
    order: int | None = None

    @field_validator("path", mode="before")
    @classmethod
    def path_to_str(cls, v: object) -> str | None:
        if v is None:
            return None
        if isinstance(v, str):
            return v
        if isinstance(v, list | dict):
            return json.dumps(v, ensure_ascii=False)
        return str(v)

    model_config = {"from_attributes": True}


class DepartmentTreeNode(BaseModel):
    """组织架构树节点（含子部门）"""
    id: UUID
    feishu_department_id: str
    name: str
    member_count: int | None = None
    leader_user_id: str | None = None
    order: int | None = None
    children: list["DepartmentTreeNode"] = []

    model_config = {"from_attributes": True}


# ── Personnel ───────────────────────────────────────────────────────


class PersonnelItem(BaseModel):
    """人员列表项"""
    id: UUID
    name: str
    en_name: str | None = None
    employee_no: str | None = None
    email: str | None = None
    enterprise_email: str | None = None
    mobile: str | None = None
    department: str | None = None
    position: str | None = None
    feishu_user_id: str | None = None
    feishu_open_id: str | None = None
    feishu_union_id: str | None = None
    avatar_url: str | None = None
    avatar_thumb: str | None = None
    avatar_middle: str | None = None
    avatar_big: str | None = None
    tenant_key: str | None = None
    feishu_department_ids: list[str] | None = None

    @field_validator("feishu_department_ids", mode="before")
    @classmethod
    def parse_dept_ids(cls, v: object) -> list[str] | None:
        if v is None:
            return None
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return None
        return None

    model_config = {"from_attributes": True}


class PersonnelListResponse(BaseModel):
    """人员分页列表"""
    items: list[PersonnelItem]
    total: int
    offset: int
    limit: int
