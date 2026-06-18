"""试剂管理 Schemas

定义试剂/标准品领用台账的请求和响应数据模型。
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AiGenReasonRequest(BaseModel):
    """AI 生成领用事由请求

    Args:
        bill_no: 领用单据编号
        user_input: 用户补充描述内容
        operator: 当前操作人账号
    """
    bill_no: str = Field(..., description="领用单据编号")
    user_input: str = Field(..., description="用户补充描述内容")
    operator: str = Field(..., description="当前操作人账号")


class AiGenScrapRequest(BaseModel):
    """AI 生成报废原因请求

    Args:
        bill_no: 报废单据编号
        user_input: 用户补充描述内容
        operator: 当前操作人账号
    """
    bill_no: str = Field(..., description="报废单据编号")
    user_input: str = Field(..., description="用户补充描述内容")
    operator: str = Field(..., description="当前操作人账号")


class AiGenResponse(BaseModel):
    """AI 生成结果响应

    Args:
        result: AI 生成的内容
        bill_no: 单据编号
        operate_type: 操作类型
    """
    result: str = Field(..., description="AI 生成的内容")
    bill_no: str = Field(..., description="单据编号")
    operate_type: str = Field(..., description="操作类型")


class AiGenErrorResponse(BaseModel):
    """AI 生成错误响应

    Args:
        code: 错误码
        message: 错误信息
    """
    code: int = Field(..., description="错误码")
    message: str = Field(..., description="错误信息")


class AiGenAnalyseRequest(BaseModel):
    """AI 试剂异常分析请求

    Args:
        bill_no: 单据编号
        reagent_name: 试剂名称
        problem_description: 问题描述
        storage_conditions: 储存条件
        operator: 当前操作人账号
    """
    bill_no: str = Field(..., description="单据编号")
    reagent_name: str = Field(..., description="试剂名称")
    problem_description: str = Field(..., description="问题描述（近效期/变质/储存异常）")
    storage_conditions: str = Field(default="", description="储存条件")
    operator: str = Field(..., description="当前操作人账号")