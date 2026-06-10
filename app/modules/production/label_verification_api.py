from datetime import date
from uuid import UUID

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import paginated_response, success_response
from app.modules.production.schemas import (
    LabelVerificationCreate,
    LabelVerificationUpdate,
)
from app.modules.production.service import LabelVerificationService
from app.shared.module_api import create_module_router
from app.shared.module_registry import MODULES_BY_CODE
from app.shared.schemas import PageParams

router = create_module_router(MODULES_BY_CODE["quality"])


def get_label_verification_service(
    session: AsyncSession = Depends(get_db),
) -> LabelVerificationService:
    return LabelVerificationService(session)


# ─── LabelVerification Routes ───


@router.get("/label-verifications", summary="标签复核记录列表")
async def list_label_verifications(
    batch_number: str | None = Query(None, description="批号搜索"),
    product_name: str | None = Query(None, description="产品名称搜索"),
    result_status: str | None = Query(None, description="结论状态筛选"),
    start_date: date | None = Query(None, description="复核日期起始"),
    end_date: date | None = Query(None, description="复核日期截止"),
    page_params: PageParams = Depends(),
    service: LabelVerificationService = Depends(get_label_verification_service),
):
    verifications, total = await service.list_verifications(
        batch_number=batch_number,
        product_name=product_name,
        result_status=result_status,
        start_date=start_date,
        end_date=end_date,
        page=page_params.page,
        page_size=page_params.page_size,
    )
    data = [v.model_dump(mode="json") for v in verifications]
    return paginated_response(
        data=data,
        page=page_params.page,
        page_size=page_params.page_size,
        total=total,
    )


@router.post("/label-verifications", summary="创建标签复核记录")
async def create_label_verification(
    payload: LabelVerificationCreate,
    service: LabelVerificationService = Depends(get_label_verification_service),
):
    verification = await service.create_verification(payload)
    return success_response(
        data=verification.model_dump(mode="json"),
        message="标签复核记录创建成功",
        status_code=201,
    )


@router.get("/label-verifications/statistics", summary="标签复核统计")
async def get_label_verification_statistics(
    service: LabelVerificationService = Depends(get_label_verification_service),
):
    stats = await service.get_statistics()
    return success_response(data=stats.model_dump(mode="json"))


@router.get(
    "/label-verifications/batch/{batch_number}",
    summary="按批号查询历史记录",
)
async def get_verifications_by_batch(
    batch_number: str,
    service: LabelVerificationService = Depends(get_label_verification_service),
):
    verifications = await service.get_by_batch_number(batch_number)
    data = [v.model_dump(mode="json") for v in verifications]
    return success_response(data=data)


@router.get(
    "/label-verifications/{verification_id}",
    summary="标签复核记录详情",
)
async def get_label_verification(
    verification_id: UUID,
    service: LabelVerificationService = Depends(get_label_verification_service),
):
    verification = await service.get_verification(verification_id)
    return success_response(
        data=verification.model_dump(mode="json"),
    )


@router.put(
    "/label-verifications/{verification_id}",
    summary="更新标签复核记录",
)
async def update_label_verification(
    verification_id: UUID,
    payload: LabelVerificationUpdate,
    service: LabelVerificationService = Depends(get_label_verification_service),
):
    verification = await service.update_verification(verification_id, payload)
    return success_response(
        data=verification.model_dump(mode="json"),
        message="标签复核记录更新成功",
    )


@router.delete(
    "/label-verifications/{verification_id}",
    summary="删除标签复核记录",
)
async def delete_label_verification(
    verification_id: UUID,
    service: LabelVerificationService = Depends(get_label_verification_service),
):
    await service.delete_verification(verification_id)
    return success_response(message="标签复核记录删除成功")
