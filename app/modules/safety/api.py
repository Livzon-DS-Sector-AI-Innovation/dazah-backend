"""Safety API routes."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import CurrentUser, get_current_user
from app.core.response import ApiResponse
from app.modules.safety.schemas import (
    AccidentCreate,
    AccidentResponse,
    AccidentUpdate,
    HazardReportCreate,
    HazardReportResponse,
    HazardReportUpdate,
    SafetyCheckCreate,
    SafetyCheckResponse,
    SafetyCheckUpdate,
    SafetyTrainingCreate,
    SafetyTrainingResponse,
    SafetyTrainingUpdate,
    TrainingRecordCreate,
    TrainingRecordResponse,
    TrainingRecordUpdate,
)
from app.modules.safety.service import SafetyService

router = APIRouter()


# ==================== 安全检查 Routes ====================


@router.get("/checks", response_model=ApiResponse, summary="获取安全检查列表")
async def get_checks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    status: str | None = None,
    check_type: str | None = None,
    department: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """获取安全检查列表"""
    service = SafetyService(db)
    skip = (page - 1) * page_size
    items, total = await service.get_checks(skip, page_size, status, check_type, department)
    return ApiResponse(
        data=[SafetyCheckResponse.model_validate(c) for c in items],
        meta={"page": page, "page_size": page_size, "total": total},
    )


@router.get("/checks/{check_id}", response_model=ApiResponse, summary="获取安全检查详情")
async def get_check(
    check_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """获取安全检查详情"""
    service = SafetyService(db)
    item = await service.get_check(check_id)
    if not item:
        return ApiResponse(code=404, message="检查记录不存在")
    return ApiResponse(data=SafetyCheckResponse.model_validate(item))


@router.post("/checks", response_model=ApiResponse, summary="创建安全检查")
async def create_check(
    data: SafetyCheckCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """创建安全检查"""
    service = SafetyService(db)
    item = await service.create_check(data)
    await db.commit()
    return ApiResponse(data=SafetyCheckResponse.model_validate(item))


@router.put("/checks/{check_id}", response_model=ApiResponse, summary="更新安全检查")
async def update_check(
    check_id: uuid.UUID,
    data: SafetyCheckUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """更新安全检查"""
    service = SafetyService(db)
    item = await service.update_check(check_id, data)
    if not item:
        return ApiResponse(code=404, message="检查记录不存在")
    await db.commit()
    return ApiResponse(data=SafetyCheckResponse.model_validate(item))


@router.post("/checks/{check_id}/submit", response_model=ApiResponse, summary="提交安全检查")
async def submit_check(
    check_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """提交安全检查（草稿→已提交）"""
    service = SafetyService(db)
    item = await service.submit_check(check_id)
    if not item:
        return ApiResponse(code=400, message="无法提交，当前状态不允许")
    await db.commit()
    return ApiResponse(data=SafetyCheckResponse.model_validate(item))


@router.post("/checks/{check_id}/review", response_model=ApiResponse, summary="审核安全检查")
async def review_check(
    check_id: uuid.UUID,
    result: str = Query(..., description="审核结果: qualified/unqualified"),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """审核安全检查"""
    service = SafetyService(db)
    item = await service.review_check(check_id, result)
    if not item:
        return ApiResponse(code=400, message="无法审核，当前状态不允许")
    await db.commit()
    return ApiResponse(data=SafetyCheckResponse.model_validate(item))


@router.delete("/checks/{check_id}", response_model=ApiResponse, summary="删除安全检查")
async def delete_check(
    check_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """删除安全检查"""
    service = SafetyService(db)
    result = await service.delete_check(check_id)
    if not result:
        return ApiResponse(code=404, message="检查记录不存在")
    await db.commit()
    return ApiResponse(message="删除成功")


# ==================== 隐患排查 Routes ====================


@router.get("/hazards", response_model=ApiResponse, summary="获取隐患列表")
async def get_hazards(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    status: str | None = None,
    hazard_type: str | None = None,
    hazard_level: str | None = None,
    department: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """获取隐患列表"""
    service = SafetyService(db)
    skip = (page - 1) * page_size
    items, total = await service.get_hazards(
        skip, page_size, status, hazard_type, hazard_level, department
    )
    return ApiResponse(
        data=[HazardReportResponse.model_validate(h) for h in items],
        meta={"page": page, "page_size": page_size, "total": total},
    )


@router.get("/hazards/{hazard_id}", response_model=ApiResponse, summary="获取隐患详情")
async def get_hazard(
    hazard_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """获取隐患详情"""
    service = SafetyService(db)
    item = await service.get_hazard(hazard_id)
    if not item:
        return ApiResponse(code=404, message="隐患不存在")
    return ApiResponse(data=HazardReportResponse.model_validate(item))


@router.post("/hazards", response_model=ApiResponse, summary="创建隐患")
async def create_hazard(
    data: HazardReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """创建隐患"""
    service = SafetyService(db)
    item = await service.create_hazard(data)
    await db.commit()
    return ApiResponse(data=HazardReportResponse.model_validate(item))


@router.put("/hazards/{hazard_id}", response_model=ApiResponse, summary="更新隐患")
async def update_hazard(
    hazard_id: uuid.UUID,
    data: HazardReportUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """更新隐患"""
    service = SafetyService(db)
    item = await service.update_hazard(hazard_id, data)
    if not item:
        return ApiResponse(code=404, message="隐患不存在")
    await db.commit()
    return ApiResponse(data=HazardReportResponse.model_validate(item))


@router.post(
    "/hazards/{hazard_id}/rectification/start",
    response_model=ApiResponse,
    summary="开始整改",
)
async def start_rectification(
    hazard_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """开始整改"""
    service = SafetyService(db)
    item = await service.start_rectification(hazard_id)
    if not item:
        return ApiResponse(code=400, message="无法开始整改，当前状态不允许")
    await db.commit()
    return ApiResponse(data=HazardReportResponse.model_validate(item))


@router.post(
    "/hazards/{hazard_id}/rectification/complete",
    response_model=ApiResponse,
    summary="完成整改",
)
async def complete_rectification(
    hazard_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """完成整改"""
    service = SafetyService(db)
    item = await service.complete_rectification(hazard_id)
    if not item:
        return ApiResponse(code=400, message="无法完成整改，当前状态不允许")
    await db.commit()
    return ApiResponse(data=HazardReportResponse.model_validate(item))


@router.post(
    "/hazards/{hazard_id}/rectification/verify",
    response_model=ApiResponse,
    summary="验证整改",
)
async def verify_rectification(
    hazard_id: uuid.UUID,
    passed: bool = Query(..., description="是否通过验证"),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """验证整改"""
    service = SafetyService(db)
    user_id = current_user.id if current_user else None
    user_name = current_user.name if current_user else None
    item = await service.verify_rectification(
        hazard_id, verified_by=user_id, verified_by_name=user_name, passed=passed
    )
    if not item:
        return ApiResponse(code=400, message="无法验证，当前状态不允许")
    await db.commit()
    return ApiResponse(data=HazardReportResponse.model_validate(item))


@router.delete("/hazards/{hazard_id}", response_model=ApiResponse, summary="删除隐患")
async def delete_hazard(
    hazard_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """删除隐患"""
    service = SafetyService(db)
    result = await service.delete_hazard(hazard_id)
    if not result:
        return ApiResponse(code=404, message="隐患不存在")
    await db.commit()
    return ApiResponse(message="删除成功")


# ==================== 事故管理 Routes ====================


@router.get("/accidents", response_model=ApiResponse, summary="获取事故列表")
async def get_accidents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    status: str | None = None,
    accident_type: str | None = None,
    accident_level: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """获取事故列表"""
    service = SafetyService(db)
    skip = (page - 1) * page_size
    items, total = await service.get_accidents(
        skip, page_size, status, accident_type, accident_level
    )
    return ApiResponse(
        data=[AccidentResponse.model_validate(a) for a in items],
        meta={"page": page, "page_size": page_size, "total": total},
    )


@router.get("/accidents/{accident_id}", response_model=ApiResponse, summary="获取事故详情")
async def get_accident(
    accident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """获取事故详情"""
    service = SafetyService(db)
    item = await service.get_accident(accident_id)
    if not item:
        return ApiResponse(code=404, message="事故不存在")
    return ApiResponse(data=AccidentResponse.model_validate(item))


@router.post("/accidents", response_model=ApiResponse, summary="创建事故")
async def create_accident(
    data: AccidentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """创建事故"""
    service = SafetyService(db)
    item = await service.create_accident(data)
    await db.commit()
    return ApiResponse(data=AccidentResponse.model_validate(item))


@router.put("/accidents/{accident_id}", response_model=ApiResponse, summary="更新事故")
async def update_accident(
    accident_id: uuid.UUID,
    data: AccidentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """更新事故"""
    service = SafetyService(db)
    item = await service.update_accident(accident_id, data)
    if not item:
        return ApiResponse(code=404, message="事故不存在")
    await db.commit()
    return ApiResponse(data=AccidentResponse.model_validate(item))


@router.post(
    "/accidents/{accident_id}/investigate",
    response_model=ApiResponse,
    summary="开始调查事故",
)
async def investigate_accident(
    accident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """开始调查事故"""
    service = SafetyService(db)
    user_id = current_user.id if current_user else None
    user_name = current_user.name if current_user else None
    item = await service.investigate_accident(accident_id, user_id, user_name)
    if not item:
        return ApiResponse(code=400, message="无法开始调查，当前状态不允许")
    await db.commit()
    return ApiResponse(data=AccidentResponse.model_validate(item))


@router.post(
    "/accidents/{accident_id}/resolve",
    response_model=ApiResponse,
    summary="处理并解决事故",
)
async def resolve_accident(
    accident_id: uuid.UUID,
    direct_cause: str = Query(..., description="直接原因"),
    root_cause: str = Query(..., description="根本原因"),
    handling_measures: str = Query(..., description="处理措施"),
    corrective_actions: str | None = Query(None, description="纠正预防措施"),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """处理并解决事故"""
    service = SafetyService(db)
    item = await service.resolve_accident(
        accident_id, direct_cause, root_cause, handling_measures, corrective_actions
    )
    if not item:
        return ApiResponse(code=400, message="无法解决，当前状态不允许")
    await db.commit()
    return ApiResponse(data=AccidentResponse.model_validate(item))


@router.post(
    "/accidents/{accident_id}/close",
    response_model=ApiResponse,
    summary="关闭事故",
)
async def close_accident(
    accident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """关闭事故"""
    service = SafetyService(db)
    item = await service.close_accident(accident_id)
    if not item:
        return ApiResponse(code=400, message="无法关闭，当前状态不允许")
    await db.commit()
    return ApiResponse(data=AccidentResponse.model_validate(item))


@router.delete("/accidents/{accident_id}", response_model=ApiResponse, summary="删除事故")
async def delete_accident(
    accident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """删除事故"""
    service = SafetyService(db)
    result = await service.delete_accident(accident_id)
    if not result:
        return ApiResponse(code=404, message="事故不存在")
    await db.commit()
    return ApiResponse(message="删除成功")


# ==================== 安全培训 Routes ====================


@router.get("/trainings", response_model=ApiResponse, summary="获取安全培训列表")
async def get_trainings(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    status: str | None = None,
    training_type: str | None = None,
    department: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """获取安全培训列表"""
    service = SafetyService(db)
    skip = (page - 1) * page_size
    items, total = await service.get_trainings(skip, page_size, status, training_type, department)
    return ApiResponse(
        data=[SafetyTrainingResponse.model_validate(t) for t in items],
        meta={"page": page, "page_size": page_size, "total": total},
    )


@router.get("/trainings/{training_id}", response_model=ApiResponse, summary="获取安全培训详情")
async def get_training(
    training_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """获取安全培训详情"""
    service = SafetyService(db)
    item = await service.get_training(training_id)
    if not item:
        return ApiResponse(code=404, message="培训不存在")
    return ApiResponse(data=SafetyTrainingResponse.model_validate(item))


@router.post("/trainings", response_model=ApiResponse, summary="创建安全培训")
async def create_training(
    data: SafetyTrainingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """创建安全培训"""
    service = SafetyService(db)
    item = await service.create_training(data)
    await db.commit()
    return ApiResponse(data=SafetyTrainingResponse.model_validate(item))


@router.put("/trainings/{training_id}", response_model=ApiResponse, summary="更新安全培训")
async def update_training(
    training_id: uuid.UUID,
    data: SafetyTrainingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """更新安全培训"""
    service = SafetyService(db)
    item = await service.update_training(training_id, data)
    if not item:
        return ApiResponse(code=404, message="培训不存在")
    await db.commit()
    return ApiResponse(data=SafetyTrainingResponse.model_validate(item))


@router.post("/trainings/{training_id}/start", response_model=ApiResponse, summary="开始培训")
async def start_training(
    training_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """开始培训（草稿→进行中）"""
    service = SafetyService(db)
    item = await service.start_training(training_id)
    if not item:
        return ApiResponse(code=400, message="无法开始培训，当前状态不允许")
    await db.commit()
    return ApiResponse(data=SafetyTrainingResponse.model_validate(item))


@router.post("/trainings/{training_id}/complete", response_model=ApiResponse, summary="完成培训")
async def complete_training(
    training_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """完成培训"""
    service = SafetyService(db)
    item = await service.complete_training(training_id)
    if not item:
        return ApiResponse(code=400, message="无法完成培训，当前状态不允许")
    await db.commit()
    return ApiResponse(data=SafetyTrainingResponse.model_validate(item))


@router.delete("/trainings/{training_id}", response_model=ApiResponse, summary="删除安全培训")
async def delete_training(
    training_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """删除安全培训"""
    service = SafetyService(db)
    result = await service.delete_training(training_id)
    if not result:
        return ApiResponse(code=404, message="培训不存在")
    await db.commit()
    return ApiResponse(message="删除成功")


# ==================== 培训记录 Routes ====================


@router.get(
    "/trainings/{training_id}/records",
    response_model=ApiResponse,
    summary="获取培训签到记录列表",
)
async def get_training_records(
    training_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """获取培训签到记录列表"""
    service = SafetyService(db)
    items = await service.get_training_records(training_id)
    return ApiResponse(data=[TrainingRecordResponse.model_validate(r) for r in items])


@router.post(
    "/trainings/{training_id}/records",
    response_model=ApiResponse,
    summary="添加培训签到记录",
)
async def create_training_record(
    training_id: uuid.UUID,
    data: TrainingRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """添加培训签到记录"""
    service = SafetyService(db)
    data.training_id = training_id
    item = await service.create_training_record(data)
    await db.commit()
    return ApiResponse(data=TrainingRecordResponse.model_validate(item))


@router.put(
    "/training-records/{record_id}",
    response_model=ApiResponse,
    summary="更新培训签到记录",
)
async def update_training_record(
    record_id: uuid.UUID,
    data: TrainingRecordUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """更新培训签到记录"""
    service = SafetyService(db)
    item = await service.update_training_record(record_id, data)
    if not item:
        return ApiResponse(code=404, message="记录不存在")
    await db.commit()
    return ApiResponse(data=TrainingRecordResponse.model_validate(item))


@router.delete(
    "/training-records/{record_id}",
    response_model=ApiResponse,
    summary="删除培训签到记录",
)
async def delete_training_record(
    record_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """删除培训签到记录"""
    service = SafetyService(db)
    result = await service.delete_training_record(record_id)
    if not result:
        return ApiResponse(code=404, message="记录不存在")
    await db.commit()
    return ApiResponse(message="删除成功")


# ==================== 枚举数据接口 ====================


@router.get("/enums", response_model=ApiResponse, summary="获取枚举值列表")
async def get_enums(
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """获取安全模块的所有枚举值选项"""
    from app.modules.safety.schemas import (
        ACCIDENT_LEVEL_OPTIONS,
        ACCIDENT_TYPE_OPTIONS,
        CHECK_TYPE_OPTIONS,
        HAZARD_LEVEL_OPTIONS,
        HAZARD_TYPE_OPTIONS,
        TRAINING_MODE_OPTIONS,
        TRAINING_TYPE_OPTIONS,
    )

    return ApiResponse(
        data={
            "check_types": CHECK_TYPE_OPTIONS,
            "hazard_types": HAZARD_TYPE_OPTIONS,
            "hazard_levels": HAZARD_LEVEL_OPTIONS,
            "accident_types": ACCIDENT_TYPE_OPTIONS,
            "accident_levels": ACCIDENT_LEVEL_OPTIONS,
            "training_types": TRAINING_TYPE_OPTIONS,
            "training_modes": TRAINING_MODE_OPTIONS,
        }
    )
