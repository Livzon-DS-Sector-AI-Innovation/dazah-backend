"""Instrument Calibration API (仪器校准管理API路由)

仪器设备台账、校准规则配置、校准记录的API接口
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.core.database import get_db
from app.core.deps import CurrentUser, get_current_user
from app.modules.quality.instrument_service import (
    InstrumentService,
    CalibrationRuleService,
    CalibrationRecordService,
)
from app.modules.quality.instrument_schemas import (
    # Instrument
    InstrumentCreate,
    InstrumentUpdate,
    InstrumentResponse,
    InstrumentListResponse,
    InstrumentListItem,
    InstrumentFilter,
    # CalibrationRule
    CalibrationRuleCreate,
    CalibrationRuleUpdate,
    CalibrationRuleResponse,
    # CalibrationRecord
    CalibrationRecordCreate,
    CalibrationRecordUpdate,
    CalibrationRecordResponse,
    CalibrationRecordListResponse,
    CalibrationRecordListItem,
    CalibrationRecordFilter,
    # Approval
    ApprovalCreate,
    ApprovalResponse,
)


class ApiResponse(BaseModel):
    """统一响应格式"""
    code: int = 200
    message: str = "Success"
    data: Optional[dict | list] = None


router = APIRouter(prefix="/instrument", tags=["仪器校准管理"])


def get_instrument_service(session = Depends(get_db)) -> InstrumentService:
    return InstrumentService(session)


def get_rule_service(session = Depends(get_db)) -> CalibrationRuleService:
    return CalibrationRuleService(session)


def get_record_service(session = Depends(get_db)) -> CalibrationRecordService:
    return CalibrationRecordService(session)


# ========== 仪器设备台账 API ==========

@router.get("", response_model=ApiResponse)
async def list_instruments(
    instrument_no: Optional[str] = Query(None, description="仪器编号"),
    instrument_name: Optional[str] = Query(None, description="仪器名称"),
    category: Optional[str] = Query(None, description="仪器分类"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    status: Optional[str] = Query(None, description="状态"),
    is_overdue: Optional[bool] = Query(None, description="是否超期"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    service: InstrumentService = Depends(get_instrument_service),
):
    """获取仪器设备列表"""
    instruments, total = await service.list_instruments(
        instrument_no=instrument_no,
        instrument_name=instrument_name,
        category=category,
        is_active=is_active,
        status=status,
        is_overdue=is_overdue,
        page=page,
        page_size=page_size
    )

    # 构建响应数据
    items = []
    for inst in instruments:
        rule_service = CalibrationRuleService(service.session)
        rule = await rule_service.repository.get_by_instrument_id(inst.id)
        is_overdue = False
        if rule and rule.next_calibration_date:
            from datetime import datetime, timezone
            # 确保比较时使用一致的时区
            now = datetime.now(timezone.utc)
            rule_date = rule.next_calibration_date
            if rule_date.tzinfo is None:
                rule_date = rule_date.replace(tzinfo=timezone.utc)
            if rule_date < now:
                is_overdue = True

        items.append(InstrumentListItem(
            id=inst.id,
            instrument_no=inst.instrument_no,
            instrument_name=inst.instrument_name,
            model=inst.model,
            category=inst.category,
            location=inst.location,
            responsible_name=inst.responsible_name,
            is_active=inst.is_active,
            status=inst.status,
            next_calibration_date=rule.next_calibration_date if rule else None,
            is_overdue=is_overdue,
            created_at=inst.created_at
        ))

    return ApiResponse(
        data={
            "items": [item.model_dump() for item in items],
            "total": total,
            "page": page,
            "page_size": page_size
        }
    )


@router.post("", response_model=ApiResponse)
async def create_instrument(
    data: InstrumentCreate,
    service: InstrumentService = Depends(get_instrument_service),
    current_user = Depends(get_current_user),
):
    """创建仪器设备"""
    try:
        user_id = current_user.id if current_user else None
        instrument = await service.create_instrument(data, user_id)
        return ApiResponse(
            message="创建成功",
            data=InstrumentResponse.model_validate(instrument).model_dump()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{instrument_id}/submit", response_model=ApiResponse)
async def submit_instrument(
    instrument_id: UUID,
    service: InstrumentService = Depends(get_instrument_service),
    current_user = Depends(get_current_user),
):
    """提交仪器审核"""
    try:
        user_id = current_user.id if current_user else None
        instrument = await service.submit_instrument(instrument_id, user_id)
        return ApiResponse(
            message="提交成功",
            data=InstrumentResponse.model_validate(instrument).model_dump()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{instrument_id}/approve", response_model=ApiResponse)
async def approve_instrument(
    instrument_id: UUID,
    approved: bool = Query(..., description="是否批准"),
    comments: Optional[str] = Query(None, description="审批意见"),
    approval_type: str = Query("admin", description="审批类型：admin/qa"),
    service: InstrumentService = Depends(get_instrument_service),
    current_user = Depends(get_current_user),
):
    """审批仪器"""
    try:
        user_id = current_user.id if current_user else None
        user_name = current_user.username if current_user else None
        instrument = await service.approve_instrument(
            instrument_id, approved, comments, approval_type, user_id, user_name
        )
        return ApiResponse(
            message="审批完成",
            data=InstrumentResponse.model_validate(instrument).model_dump()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{instrument_id}/activate", response_model=ApiResponse)
async def activate_instrument(
    instrument_id: UUID,
    service: InstrumentService = Depends(get_instrument_service),
    current_user = Depends(get_current_user),
):
    """启用仪器"""
    try:
        user_id = current_user.id if current_user else None
        instrument = await service.activate_instrument(instrument_id, user_id)
        return ApiResponse(
            message="启用成功",
            data=InstrumentResponse.model_validate(instrument).model_dump()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{instrument_id}/deactivate", response_model=ApiResponse)
async def deactivate_instrument(
    instrument_id: UUID,
    reason: str = Query(..., description="停用原因"),
    service: InstrumentService = Depends(get_instrument_service),
    current_user = Depends(get_current_user),
):
    """停用仪器"""
    try:
        user_id = current_user.id if current_user else None
        instrument = await service.deactivate_instrument(instrument_id, reason, user_id)
        return ApiResponse(
            message="停用成功",
            data=InstrumentResponse.model_validate(instrument).model_dump()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ========== 校准规则 API ==========

@router.get("/rules/{instrument_id}", response_model=ApiResponse)
async def get_calibration_rule(
    instrument_id: UUID,
    service: CalibrationRuleService = Depends(get_rule_service),
):
    """获取仪器校准规则"""
    rule = await service.repository.get_by_instrument_id(instrument_id)
    if rule:
        return ApiResponse(data=CalibrationRuleResponse.model_validate(rule).model_dump())
    return ApiResponse(data=None)


@router.post("/rules", response_model=ApiResponse)
async def create_calibration_rule(
    data: CalibrationRuleCreate,
    service: CalibrationRuleService = Depends(get_rule_service),
    current_user = Depends(get_current_user),
):
    """创建校准规则"""
    try:
        user_id = current_user.id if current_user else None
        rule = await service.create_rule(data, user_id)
        return ApiResponse(
            message="创建成功",
            data=CalibrationRuleResponse.model_validate(rule).model_dump()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/rules/{rule_id}", response_model=ApiResponse)
async def update_calibration_rule(
    rule_id: UUID,
    data: CalibrationRuleUpdate,
    service: CalibrationRuleService = Depends(get_rule_service),
    current_user = Depends(get_current_user),
):
    """更新校准规则"""
    try:
        user_id = current_user.id if current_user else None
        rule = await service.update_rule(rule_id, data, user_id)
        return ApiResponse(
            message="更新成功",
            data=CalibrationRuleResponse.model_validate(rule).model_dump()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/rules/{rule_id}")
async def delete_calibration_rule(
    rule_id: UUID,
    service: CalibrationRuleService = Depends(get_rule_service),
):
    """删除校准规则"""
    try:
        await service.delete_rule(rule_id)
        return {"message": "删除成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/upcoming", response_model=ApiResponse)
async def get_upcoming_calibrations(
    days: int = Query(30, description="提前预警天数"),
    service: CalibrationRuleService = Depends(get_rule_service),
):
    """获取即将到期的校准计划"""
    rules = await service.get_upcoming_calibrations(days)
    return ApiResponse(data=[
        {
            "id": str(rule.id),
            "instrument_id": str(rule.instrument_id),
            "instrument_name": rule.instrument.instrument_name if rule.instrument else None,
            "calibration_method": rule.calibration_method,
            "next_calibration_date": rule.next_calibration_date.isoformat() if rule.next_calibration_date else None,
            "warning_days": rule.warning_days,
        }
        for rule in rules
    ])


# ========== 校准记录 API ==========

@router.get("/records", response_model=ApiResponse)
async def list_calibration_records(
    instrument_id: Optional[str] = Query(None, description="仪器ID"),
    calibration_no: Optional[str] = Query(None, description="校准单据编号"),
    calibration_result: Optional[str] = Query(None, description="校准结论"),
    status: Optional[str] = Query(None, description="状态"),
    calibration_method: Optional[str] = Query(None, description="校准方式"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    service: CalibrationRecordService = Depends(get_record_service),
):
    """获取校准记录列表"""
    from datetime import datetime

    # 直接使用字符串instrument_id，让service层处理转换
    start_dt = datetime.fromisoformat(start_date) if start_date else None
    end_dt = datetime.fromisoformat(end_date) if end_date else None

    records, total = await service.list_records(
        instrument_id=instrument_id,
        calibration_no=calibration_no,
        calibration_result=calibration_result,
        status=status,
        calibration_method=calibration_method,
        start_date=start_dt,
        end_date=end_dt,
        page=page,
        page_size=page_size
    )

    # 获取仪器信息
    instrument_service = InstrumentService(service.session)
    items = []
    for record in records:
        instrument = await instrument_service.repository.get_by_id(record.instrument_id)
        items.append({
            "id": str(record.id),
            "calibration_no": record.calibration_no,
            "instrument_id": str(record.instrument_id),
            "instrument_no": instrument.instrument_no if instrument else None,
            "instrument_name": instrument.instrument_name if instrument else None,
            "calibration_date": record.calibration_date.isoformat() if record.calibration_date else None,
            "calibration_method": record.calibration_method,
            "calibration_result": record.calibration_result,
            "status": record.status,
            "calibrator_name": record.calibrator_name,
            "certificate_no": record.certificate_no,
            "created_at": record.created_at.isoformat() if record.created_at else None,
        })

    return ApiResponse(data={
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    })


@router.get("/records/{record_id}", response_model=ApiResponse)
async def get_calibration_record(
    record_id: UUID,
    service: CalibrationRecordService = Depends(get_record_service),
):
    """获取校准记录详情"""
    try:
        record = await service.get_record(record_id)
        return ApiResponse(data=CalibrationRecordResponse.model_validate(record).model_dump())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/records", response_model=ApiResponse)
async def create_calibration_record(
    data: CalibrationRecordCreate,
    service: CalibrationRecordService = Depends(get_record_service),
    current_user = Depends(get_current_user),
):
    """创建校准记录"""
    try:
        user_id = current_user.id if current_user else None
        record = await service.create_record(data, user_id)
        return ApiResponse(
            message="创建成功",
            data=CalibrationRecordResponse.model_validate(record).model_dump()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/records/{record_id}", response_model=ApiResponse)
async def update_calibration_record(
    record_id: UUID,
    data: CalibrationRecordUpdate,
    service: CalibrationRecordService = Depends(get_record_service),
    current_user = Depends(get_current_user),
):
    """更新校准记录"""
    try:
        user_id = current_user.id if current_user else None
        record = await service.update_record(record_id, data, user_id)
        return ApiResponse(
            message="更新成功",
            data=CalibrationRecordResponse.model_validate(record).model_dump()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/records/{record_id}")
async def delete_calibration_record(
    record_id: UUID,
    service: CalibrationRecordService = Depends(get_record_service),
):
    """删除校准记录"""
    try:
        await service.delete_record(record_id)
        return {"message": "删除成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/records/{record_id}/submit", response_model=ApiResponse)
async def submit_calibration_record(
    record_id: UUID,
    service: CalibrationRecordService = Depends(get_record_service),
    current_user = Depends(get_current_user),
):
    """提交校准记录"""
    try:
        user_id = current_user.id if current_user else None
        record = await service.submit_record(record_id, user_id)
        return ApiResponse(
            message="提交成功",
            data=CalibrationRecordResponse.model_validate(record).model_dump()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/records/{record_id}/approve", response_model=ApiResponse)
async def approve_calibration_record(
    record_id: UUID,
    approved: bool = Query(..., description="是否批准"),
    comments: Optional[str] = Query(None, description="审批意见"),
    approval_type: str = Query("admin", description="审批类型：admin/qa"),
    service: CalibrationRecordService = Depends(get_record_service),
    current_user = Depends(get_current_user),
):
    """审批校准记录"""
    try:
        user_id = current_user.id if current_user else None
        user_name = current_user.username if current_user else None
        record = await service.approve_record(
            record_id, approved, comments, approval_type, user_id, user_name
        )
        return ApiResponse(
            message="审批完成",
            data=CalibrationRecordResponse.model_validate(record).model_dump()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ========== 仪器设备详情/更新/删除 API (必须在/records之后) ==========

@router.get("/{instrument_id}", response_model=ApiResponse)
async def get_instrument(
    instrument_id: UUID,
    service: InstrumentService = Depends(get_instrument_service),
):
    """获取仪器详情"""
    try:
        instrument = await service.get_instrument(instrument_id)
        return ApiResponse(data=InstrumentResponse.model_validate(instrument).model_dump())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{instrument_id}", response_model=ApiResponse)
async def update_instrument(
    instrument_id: UUID,
    data: InstrumentUpdate,
    service: InstrumentService = Depends(get_instrument_service),
    current_user = Depends(get_current_user),
):
    """更新仪器设备"""
    try:
        user_id = current_user.id if current_user else None
        instrument = await service.update_instrument(instrument_id, data, user_id)
        return ApiResponse(
            message="更新成功",
            data=InstrumentResponse.model_validate(instrument).model_dump()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{instrument_id}")
async def delete_instrument(
    instrument_id: UUID,
    service: InstrumentService = Depends(get_instrument_service),
):
    """删除仪器设备"""
    try:
        await service.delete_instrument(instrument_id)
        return {"message": "删除成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))