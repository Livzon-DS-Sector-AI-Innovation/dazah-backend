"""试剂管理 API

提供试剂/标准品领用台账的 AI 辅助接口。
接口清单：
- POST /reagent/ai/gen/reason  自动生成合规领用事由
- POST /reagent/ai/gen/scrap   自动生成标准报废原因
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import error_response, success_response
from app.modules.warehouse.reagent_schemas import (
    AiGenReasonRequest,
    AiGenScrapRequest,
    AiGenAnalyseRequest,
    AiGenResponse,
)
from app.modules.warehouse.reagent_service import ReagentService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reagent", tags=["试剂管理"])


def get_reagent_service(session: AsyncSession = Depends(get_db)) -> ReagentService:
    """获取试剂服务实例

    Args:
        session: 数据库会话

    Returns:
        ReagentService 实例
    """
    return ReagentService(session)


@router.post(
    "/ai/gen/reason",
    response_model=dict,
    summary="AI 生成合规领用事由",
    description="根据用户补充描述内容，自动生成符合 GMP 规范的试剂领用事由",
)
async def generate_reason(
    request: AiGenReasonRequest,
    service: ReagentService = Depends(get_reagent_service),
) -> dict:
    """AI 生成合规领用事由接口

    Args:
        request: 请求参数（单据编号、用户补充描述、操作人账号）
        service: 试剂服务

    Returns:
        统一格式响应，包含 AI 生成结果
    """
    try:
        result = await service.generate_reason(
            bill_no=request.bill_no,
            user_input=request.user_input,
            operator=request.operator,
        )
        return success_response(data=result)

    except ValueError as e:
        # 参数校验错误
        logger.warning(f"参数校验失败: {e}")
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    except Exception as e:
        # 其他异常统一处理
        logger.error(f"AI 生成领用事由异常: {e}")
        return error_response(
            message=f"AI服务暂时不可用，请手动填写",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post(
    "/ai/gen/scrap",
    response_model=dict,
    summary="AI 生成标准报废原因",
    description="根据试剂实际情况，生成符合实验室台账要求的标准报废原因描述",
)
async def generate_scrap(
    request: AiGenScrapRequest,
    service: ReagentService = Depends(get_reagent_service),
) -> dict:
    """AI 生成标准报废原因接口

    Args:
        request: 请求参数（单据编号、用户补充描述、操作人账号）
        service: 试剂服务

    Returns:
        统一格式响应，包含 AI 生成结果
    """
    try:
        result = await service.generate_scrap(
            bill_no=request.bill_no,
            user_input=request.user_input,
            operator=request.operator,
        )
        return success_response(data=result)

    except ValueError as e:
        # 参数校验错误
        logger.warning(f"参数校验失败: {e}")
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    except Exception as e:
        # 其他异常统一处理
        logger.error(f"AI 生成报废原因异常: {e}")
        return error_response(
            message=f"AI服务暂时不可用，请手动填写",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post(
    "/ai/gen/analyse",
    response_model=dict,
    summary="AI 试剂异常分析",
    description="针对近效期、变质、储存异常等问题，分析原因并给出处置建议",
)
async def generate_analyse(
    request: AiGenAnalyseRequest,
    service: ReagentService = Depends(get_reagent_service),
) -> dict:
    """AI 试剂异常分析接口

    Args:
        request: 请求参数（单据编号、试剂名称、问题描述、储存条件、操作人账号）
        service: 试剂服务

    Returns:
        统一格式响应，包含 AI 分析结果
    """
    try:
        result = await service.generate_analyse(
            bill_no=request.bill_no,
            reagent_name=request.reagent_name,
            problem_description=request.problem_description,
            storage_conditions=request.storage_conditions,
            operator=request.operator,
        )
        return success_response(data=result)

    except ValueError as e:
        # 参数校验错误
        logger.warning(f"参数校验失败: {e}")
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    except Exception as e:
        # 其他异常统一处理
        logger.error(f"AI 试剂异常分析异常: {e}")
        return error_response(
            message=f"AI服务暂时不可用，请手动填写",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )