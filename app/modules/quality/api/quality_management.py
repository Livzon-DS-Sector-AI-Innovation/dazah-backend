"""Quality management API endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.quality.schemas import (
    CreateAttachmentReviewRequest,
    CapaApprovalRequest,
    CapaDetail,
    CapaListItem,
    CapaStatistics,
    CreateCapaRequest,
    CreateDepartmentContactRequest,
    CreateDeviationRequest,
    DeviationDetail,
    DeviationListItem,
    DeviationStatistics,
    SubmitInvestigationRequest,
    SubmitReviewRequest,
    UpdateCapaRequest,
    UpdateDepartmentContactRequest,
    UpdateDeviationRequest,
)
from app.modules.quality import service

router = APIRouter()


# ============ Deviations ============
@router.get("/deviations", summary="获取偏差列表")
async def list_deviations(
    status: str | None = None,
    level: str | None = None,
    department: str | None = None,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await service.get_deviation_list(db, status, level, department, keyword, page, page_size)
    return {"data": result["items"], "meta": {"total": result["total"], "page": result["page"], "page_size": result["page_size"]}}


@router.get("/deviations/{deviation_id}", summary="获取偏差详情")
async def get_deviation(deviation_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        detail = await service.get_deviation_detail(db, deviation_id)
        return {"data": detail.model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/deviations", summary="创建偏差")
async def create_deviation(data: CreateDeviationRequest, db: AsyncSession = Depends(get_db)) -> dict:
    result = await service.create_deviation(db, data, "system")
    return {"data": result}


@router.put("/deviations/{deviation_id}", summary="更新偏差")
async def update_deviation(deviation_id: uuid.UUID, data: UpdateDeviationRequest, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        result = await service.update_deviation(db, deviation_id, data, "system")
        return {"data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/deviations/{deviation_id}", summary="删除偏差")
async def delete_deviation(deviation_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        result = await service.delete_deviation(db, deviation_id)
        return {"data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/deviations/{deviation_id}/submit-investigation", summary="提交调查报告")
async def submit_investigation(deviation_id: uuid.UUID, data: SubmitInvestigationRequest, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        result = await service.submit_investigation(db, deviation_id, data, "system")
        return {"data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/deviations/{deviation_id}/submit-review", summary="提交审核意见")
async def submit_review(deviation_id: uuid.UUID, data: SubmitReviewRequest, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        result = await service.submit_review(db, deviation_id, data, "system")
        return {"data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/deviations/{deviation_id}/submit-final-code", summary="提交最终编号")
async def submit_final_code(deviation_id: uuid.UUID, final_code: str, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        result = await service.submit_final_code(db, deviation_id, final_code, "system")
        return {"data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/deviations/{deviation_id}/resubmit", summary="重新提交偏差")
async def resubmit_deviation(deviation_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        result = await service.resubmit_deviation(db, deviation_id, "system")
        return {"data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============ CAPAs ============
@router.get("/capas", summary="获取CAPA列表")
async def list_capas(
    status: str | None = None,
    source: str | None = None,
    category: str | None = None,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await service.get_capa_list(db, status, source, category, keyword, page, page_size)
    return {"data": result["items"], "meta": {"total": result["total"], "page": result["page"], "page_size": result["page_size"]}}


@router.get("/capas/{capa_id}", summary="获取CAPA详情")
async def get_capa(capa_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        detail = await service.get_capa_detail(db, capa_id)
        return {"data": detail.model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/capas", summary="创建CAPA")
async def create_capa(data: CreateCapaRequest, db: AsyncSession = Depends(get_db)) -> dict:
    result = await service.create_capa(db, data, "system")
    return {"data": result}


@router.put("/capas/{capa_id}", summary="更新CAPA")
async def update_capa(capa_id: uuid.UUID, data: UpdateCapaRequest, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        result = await service.update_capa(db, capa_id, data, "system")
        return {"data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/capas/{capa_id}", summary="删除CAPA")
async def delete_capa(capa_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        result = await service.delete_capa(db, capa_id)
        return {"data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============ Department Contacts ============
@router.get("/department-contacts", summary="获取部门联系人列表")
async def list_department_contacts(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await service.get_department_contact_list(db, page, page_size)
    return {"data": result["items"], "meta": {"total": result["total"], "page": result["page"], "page_size": result["page_size"]}}


@router.post("/department-contacts", summary="创建/更新部门联系人")
async def upsert_department_contact(data: CreateDepartmentContactRequest, db: AsyncSession = Depends(get_db)) -> dict:
    result = await service.upsert_department_contact(db, data, None, "system")
    return {"data": result}


@router.delete("/department-contacts/{contact_id}", summary="删除部门联系人")
async def delete_department_contact(contact_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        result = await service.delete_department_contact(db, contact_id)
        return {"data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============ Statistics ============
@router.get("/statistics/deviations", summary="获取偏差统计")
async def get_deviation_statistics(db: AsyncSession = Depends(get_db)) -> dict:
    stats = await service.get_deviation_statistics(db)
    return {"data": stats.model_dump()}


@router.get("/statistics/capas", summary="获取CAPA统计")
async def get_capa_statistics(db: AsyncSession = Depends(get_db)) -> dict:
    stats = await service.get_capa_statistics(db)
    return {"data": stats.model_dump()}


# ============ Attachment Reviews ============
@router.get("/attachment-reviews", summary="获取附件审阅列表")
async def list_attachment_reviews(
    deviation_id: uuid.UUID | None = None,
    capa_id: uuid.UUID | None = None,
    attachment_url: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> dict:
    items = await service.list_attachment_reviews(db, deviation_id, capa_id, attachment_url)
    return {"data": items}


@router.post("/attachment-reviews", summary="创建附件审阅")
async def create_attachment_review(
    data: CreateAttachmentReviewRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await service.create_attachment_review(db, data, "system")
    return {"data": result}


@router.delete("/attachment-reviews/{review_id}", summary="删除附件审阅")
async def delete_attachment_review(review_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        await service.delete_attachment_review(db, review_id)
        return {"data": {"success": True}}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
