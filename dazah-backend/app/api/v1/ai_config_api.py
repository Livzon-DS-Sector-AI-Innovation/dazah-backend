"""AI 配置管理 API

提供 AI 配置的查询和管理功能，支持数据库持久化。
"""

import re
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.platform.database import get_db_session
from app.core.ai_config import (
    get_config,
    update_config_and_save,
    get_minimax_api_key,
    get_minimax_base_url,
    get_vision_model,
)

router = APIRouter(prefix="/config", tags=["AI配置"])


class AIConfigResponse(BaseModel):
    """AI配置响应"""
    minimax_api_key: str
    minimax_base_url: str
    minimax_text_model: str
    minimax_vision_model: str
    enable_ai_reason: bool
    enable_ai_scrap: bool
    enable_ai_analyse: bool
    enable_ai_label_recognize: bool
    temperature: float
    max_tokens: int
    timeout: int


class AIConfigUpdateRequest(BaseModel):
    """AI配置更新请求"""
    minimax_api_key: str
    minimax_base_url: str
    minimax_text_model: str
    minimax_vision_model: str
    enable_ai_reason: bool
    enable_ai_scrap: bool
    enable_ai_analyse: bool
    enable_ai_label_recognize: bool
    temperature: float
    max_tokens: int
    timeout: int

    @field_validator("minimax_api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """验证API Key格式"""
        # 如果是空字符串，允许保存（用户可能想清除配置）
        if not v or not v.strip():
            return v

        # 检查是否包含中文字符（用户经常复制错误信息作为API Key）
        if re.search(r'[\u4e00-\u9fff]', v):
            raise ValueError("API Key不能包含中文字符，请确保复制的是正确的API密钥")

        # 检查长度是否过短（有效API Key通常超过20个字符）
        stripped = v.strip()
        if len(stripped) < 20:
            raise ValueError("API Key长度不足，请确保复制的是完整的API密钥")

        # 检查是否包含明显的错误提示文本
        error_keywords = ["错误", "失败", "成功", "置信度", "识别", "error", "fail", "success"]
        for keyword in error_keywords:
            if keyword.lower() in stripped.lower():
                raise ValueError(f"API Key格式不正确，请确保复制的是API密钥而非其他内容")

        return stripped


@router.get("", response_model=dict, summary="获取AI配置")
async def get_ai_config(session: AsyncSession = Depends(get_db_session)):
    """获取当前AI配置"""
    return {
        "code": 200,
        "message": "success",
        "data": get_config(),
    }


@router.post("", response_model=dict, summary="保存AI配置")
async def save_ai_config(
    request: AIConfigUpdateRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """保存AI配置（持久化到数据库）"""
    try:
        success = await update_config_and_save(request.model_dump())
    except ValueError as e:
        # 验证错误
        return {
            "code": 400,
            "message": str(e),
            "data": None,
        }

    if success:
        return {
            "code": 200,
            "message": "配置已保存到数据库",
            "data": get_config(),
        }
    else:
        return {
            "code": 500,
            "message": "配置保存失败",
            "data": None,
        }