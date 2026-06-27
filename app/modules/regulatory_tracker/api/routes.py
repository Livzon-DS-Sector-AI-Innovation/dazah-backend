"""Regulatory Tracker API routes V2 - 原料药企业影响评估。"""

import uuid
from datetime import date

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.regulatory_tracker import repository as repo
from app.modules.regulatory_tracker.services.ai_analysis_service import analyze_new_documents, analyze_and_update
from app.modules.regulatory_tracker.utils.excel_export import generate_regulatory_excel
from app.modules.regulatory_tracker.schemas import (
    RegulatoryDocumentRead,
    SyncJobRead,
    SyncTriggerRequest,
    BatchReadRequest,
)

router = APIRouter()


def _extract_impact_data(doc) -> dict:
    """从文档中提取影响评估数据。"""
    from app.modules.regulatory_tracker.services.ai_analysis_service import score_to_impact_level
    
    key_points = doc.ai_key_points or {}
    score = doc.ai_relevance_score or 0.0
    
    if isinstance(key_points, dict):
        # 优先使用 key_points 中的 impact_level，否则根据 score 计算
        impact_level = key_points.get("impact_level") or score_to_impact_level(score)
        return {
            "impact_level": impact_level,
            "impact_score": score,
            "lifecycle_impacts": key_points.get("lifecycle_impacts", []),
            "departments": key_points.get("departments", []),
            "ctd_sections": key_points.get("ctd_sections", []),
            "recommended_actions": key_points.get("recommended_actions", []),
            "notification_required": key_points.get("notification_required", False),
        }
    
    # 旧数据格式或无结构化数据
    return {
        "impact_level": score_to_impact_level(score) if score > 0 else "low",
        "impact_score": score,
        "lifecycle_impacts": [],
        "departments": [],
        "ctd_sections": [],
        "recommended_actions": [],
        "notification_required": False,
    }


# ============ Dashboard ============

@router.get("/regulatory-tracker/dashboard", summary="Dashboard 统计数据")
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    """
    返回 Dashboard 完整数据：
    - 今日/本周新增、未读、AI 已分析数量
    - 高/中影响法规数量、未分析法规数量
    - 近 7 天趋势
    - 分类统计
    - 数据来源状态
    - 今日新增法规列表
    - 重点关注法规列表（high/medium impact）
    """
    stats = await repo.get_dashboard_stats(db)
    trend = await repo.get_7day_trend(db)
    classification = await repo.get_classification_stats(db)
    source_status = await repo.get_source_status(db)
    today_docs = await repo.get_today_new_documents(db, limit=10)
    
    # 获取影响等级统计
    impact_stats = await repo.get_impact_stats(db)
    
    # 获取重点关注法规（high/medium impact）
    priority_docs = await repo.get_priority_documents(db, limit=10)

    # 格式化今日新增文档
    today_new_documents = []
    for doc in today_docs:
        source = await repo.get_data_source_by_id(db, doc.source_id)
        channel = await repo.get_channel_by_id(db, doc.channel_id)
        impact_data = _extract_impact_data(doc)
        today_new_documents.append({
            "id": str(doc.id),
            "title": doc.title,
            "publishDate": doc.publish_date.isoformat() if doc.publish_date else None,
            "classification": doc.classification,
            "statusText": doc.status_text,
            "sourceName": source.name if source else None,
            "channelName": channel.name if channel else None,
            "isNew": doc.is_new,
            "aiRelevanceScore": doc.ai_relevance_score,
            "impact_level": impact_data["impact_level"],
            "impact_score": impact_data["impact_score"],
        })

    # 格式化重点关注法规
    priority_documents = []
    for doc in priority_docs:
        source = await repo.get_data_source_by_id(db, doc.source_id)
        channel = await repo.get_channel_by_id(db, doc.channel_id)
        impact_data = _extract_impact_data(doc)
        priority_documents.append({
            "id": str(doc.id),
            "title": doc.title,
            "publishDate": doc.publish_date.isoformat() if doc.publish_date else None,
            "classification": doc.classification,
            "statusText": doc.status_text,
            "sourceName": source.name if source else None,
            "channelName": channel.name if channel else None,
            "impact_level": impact_data["impact_level"],
            "impact_score": impact_data["impact_score"],
            "lifecycle_impact": [
                lp.get("area", "") for lp in impact_data["lifecycle_impacts"]
                if isinstance(lp, dict) and lp.get("affected")
            ],
            "departments": impact_data["departments"],
            "recommended_actions": impact_data["recommended_actions"],
            "ai_summary": doc.ai_summary,
        })

    return {
        "code": 200,
        "message": "success",
        "data": {
            **stats,
            "highImpactCount": impact_stats.get("high", 0),
            "mediumImpactCount": impact_stats.get("medium", 0),
            "unanalyzedCount": impact_stats.get("unanalyzed", 0),
            "trend7Days": trend,
            "byClassification": classification,
            "sourceStatus": source_status,
            "todayNewDocuments": today_new_documents,
            "priorityDocuments": priority_documents,
        },
    }


# ============ 统计摘要（保留） ============

@router.get("/regulatory-tracker/summary", summary="法规追踪统计摘要")
async def get_summary(db: AsyncSession = Depends(get_db)):
    stats = await repo.get_summary_stats(db)
    return {
        "code": 200,
        "message": "success",
        "data": stats,
    }


# ============ 法规文档列表 ============

@router.get("/regulatory-documents", summary="法规文档列表")
async def list_documents(
    keyword: str | None = Query(None, description="关键词搜索"),
    publishDateFrom: date | None = Query(None, description="发布日期起始"),
    publishDateTo: date | None = Query(None, description="发布日期结束"),
    statusText: str | None = Query(None, description="状态筛选"),
    classification: str | None = Query(None, description="分类筛选"),
    isNew: bool | None = Query(None, description="是否新增"),
    impactLevel: str | None = Query(None, description="影响等级筛选: high/medium/low/none/unanalyzed"),
    notificationRequired: bool | None = Query(None, description="是否需要通知"),
    sourceId: uuid.UUID | None = Query(None, description="数据源 ID"),
    channelId: uuid.UUID | None = Query(None, description="栏目 ID"),
    sortBy: str = Query("publish_date", description="排序字段"),
    sortOrder: str = Query("desc", description="排序方向"),
    page: int = Query(1, ge=1, description="页码"),
    pageSize: int = Query(20, ge=1, le=100, description="每页条数"),
    db: AsyncSession = Depends(get_db),
):
    """获取法规文档列表，支持多种筛选条件、排序和分页。"""
    documents, total = await repo.get_documents_with_filters(
        db=db,
        keyword=keyword,
        publish_date_from=publishDateFrom,
        publish_date_to=publishDateTo,
        status_text=statusText,
        classification=classification,
        is_new=isNew,
        impact_level=impactLevel,
        notification_required=notificationRequired,
        source_id=sourceId,
        channel_id=channelId,
        sort_by=sortBy,
        sort_order=sortOrder,
        page=page,
        page_size=pageSize,
    )

    items = []
    for doc in documents:
        impact_data = _extract_impact_data(doc)
        items.append({
            "id": str(doc.id),
            "sourceId": str(doc.source_id),
            "channelId": str(doc.channel_id),
            "documentId": doc.document_id,
            "title": doc.title,
            "publishDate": doc.publish_date.isoformat() if doc.publish_date else None,
            "statusText": doc.status_text,
            "classification": doc.classification,
            "originalUrl": doc.original_url,
            "isNew": doc.is_new,
            "isRead": doc.is_read,
            "firstFoundAt": doc.first_found_at.isoformat() if doc.first_found_at else None,
            "lastCheckedAt": doc.last_checked_at.isoformat() if doc.last_checked_at else None,
            "createdAt": doc.created_at.isoformat() if doc.created_at else None,
            "aiSummary": doc.ai_summary,
            "aiKeyPoints": doc.ai_key_points,
            "aiRelevanceScore": doc.ai_relevance_score,
            "aiAnalyzedAt": doc.ai_analyzed_at.isoformat() if doc.ai_analyzed_at else None,
            "aiAnalysisStatus": doc.ai_analysis_status,
            "impact_level": impact_data["impact_level"],
            "impact_score": impact_data["impact_score"],
            "notification_required": impact_data["notification_required"],
        })

    return {
        "code": 200,
        "message": "success",
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "pageSize": pageSize,
            "totalPages": (total + pageSize - 1) // pageSize if pageSize > 0 else 0,
        },
    }


# ============ 法规文档详情 ============

@router.get("/regulatory-documents/{doc_id}/detail", summary="法规文档详情")
async def get_document_detail(doc_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """获取法规文档详情，包含来源和栏目名称。"""
    detail = await repo.get_document_detail(db, doc_id)
    if not detail:
        return {"code": 404, "message": "文档不存在", "data": None}

    # 获取相关法规
    doc = await repo.get_document_by_id(db, doc_id)
    related_docs = []
    if doc:
        related = await repo.get_related_documents(db, doc, limit=5)
        for rdoc in related:
            related_docs.append({
                "id": str(rdoc.id),
                "title": rdoc.title,
                "publishDate": rdoc.publish_date.isoformat() if rdoc.publish_date else None,
                "classification": rdoc.classification,
            })
    detail["relatedDocuments"] = related_docs

    return {"code": 200, "message": "success", "data": detail}


# ============ Excel 导出 ============

@router.get("/regulatory-documents/export", summary="导出法规文档为 Excel")
async def export_documents(
    format: str = Query("xlsx", description="导出格式"),
    keyword: str | None = Query(None),
    publishDateFrom: date | None = Query(None),
    publishDateTo: date | None = Query(None),
    statusText: str | None = Query(None),
    classification: str | None = Query(None),
    isNew: bool | None = Query(None),
    sourceId: uuid.UUID | None = Query(None),
    channelId: uuid.UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """导出法规文档为 Excel 文件。"""
    documents, _ = await repo.get_documents_with_filters(
        db=db,
        keyword=keyword,
        publish_date_from=publishDateFrom,
        publish_date_to=publishDateTo,
        status_text=statusText,
        classification=classification,
        is_new=isNew,
        source_id=sourceId,
        channel_id=channelId,
        page=1,
        page_size=10000,
    )

    excel_file = generate_regulatory_excel(documents)

    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=regulatory_documents.xlsx"},
    )


# ============ 标记已读 ============

@router.patch("/regulatory-documents/{doc_id}/read", summary="标记文档为已读")
async def mark_document_read(doc_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """标记单个文档为已读"""
    doc = await repo.get_document_by_id(db, doc_id)
    if not doc:
        return {"code": 404, "message": "文档不存在", "data": None}

    await repo.update_document(db, doc_id, {"is_new": False, "is_read": True})
    await db.commit()
    return {"code": 200, "message": "success", "data": {"id": str(doc_id)}}


# ============ 批量标记已读 ============

@router.post("/regulatory-documents/batch-read", summary="批量标记文档已读")
async def batch_mark_read(request: BatchReadRequest, db: AsyncSession = Depends(get_db)):
    """批量标记文档为已读"""
    count = await repo.batch_mark_read(db, request.documentIds)
    await db.commit()
    return {"code": 200, "message": "success", "data": {"updatedCount": count}}


# ============ 手动触发同步 ============

@router.post("/sync-jobs/trigger", summary="手动触发同步任务")
async def trigger_sync_job(
    request: SyncTriggerRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """手动触发数据源同步任务（后台异步执行）"""
    source = await repo.get_data_source_by_code(db, request.sourceCode)
    if not source:
        return {"code": 404, "message": f"数据源 {request.sourceCode} 不存在", "data": None}

    channel = await repo.get_channel_by_code(db, source.id, request.channelCode)
    if not channel:
        return {"code": 404, "message": f"栏目 {request.channelCode} 不存在", "data": None}

    if not source.enabled or not channel.enabled:
        return {"code": 400, "message": "数据源或栏目已禁用", "data": None}

    # 创建同步任务记录
    job = await repo.create_sync_job(db, {
        "source_id": source.id,
        "channel_id": channel.id,
        "job_type": "manual_sync",
        "status": "pending",
    })
    await db.commit()

    # 后台执行同步（不阻塞响应）
    from app.modules.regulatory_tracker.services.sync_service import run_sync_job

    async def _run_sync():
        from app.core.database import async_session_factory
        async with async_session_factory() as session:
            new_docs = await run_sync_job(
                db=session,
                source=source,
                channel=channel,
                job_type="manual_sync",
                start_page=request.startPage,
                end_page=request.endPage,
            )
            
            # 如果 autoAnalyze=true，自动分析新增法规（限前 5 条）
            if request.autoAnalyze:
                sync_result = new_docs  # new_docs 现在是 run_sync_job 的返回值
                new_doc_list = sync_result.get("new_docs", []) if isinstance(sync_result, dict) else []
                docs_to_analyze = new_doc_list[:5]
                for doc in docs_to_analyze:
                    try:
                        await analyze_and_update(session, doc)
                    except Exception as e:
                        # 分析失败不影响法规入库
                        import logging
                        logging.getLogger(__name__).error(f"自动分析失败 [{doc.document_id}]: {e}")

    background_tasks.add_task(_run_sync)

    return {
        "code": 200,
        "message": "同步任务已创建",
        "data": {
            "jobId": str(job.id),
            "status": "pending",
            "sourceCode": request.sourceCode,
            "channelCode": request.channelCode,
            "autoAnalyze": request.autoAnalyze,
        },
    }


# ============ 同步任务列表 ============

@router.get("/sync-jobs", summary="同步任务列表")
async def list_sync_jobs(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """获取同步任务日志列表"""
    jobs, total = await repo.get_sync_jobs_list(db=db, page=page, page_size=pageSize)

    items = []
    for job in jobs:
        items.append({
            "id": str(job.id),
            "sourceId": str(job.source_id),
            "channelId": str(job.channel_id),
            "jobType": job.job_type,
            "startedAt": job.started_at.isoformat() if job.started_at else None,
            "finishedAt": job.finished_at.isoformat() if job.finished_at else None,
            "status": job.status,
            "totalPages": job.total_pages,
            "checkedCount": job.checked_count,
            "newCount": job.new_count,
            "updatedCount": job.updated_count,
            "errorMessage": job.error_message,
            "createdAt": job.created_at.isoformat() if job.created_at else None,
        })

    return {
        "code": 200,
        "message": "success",
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "pageSize": pageSize,
            "totalPages": (total + pageSize - 1) // pageSize if pageSize > 0 else 0,
        },
    }


# ============ AI 分析 ============

@router.post("/regulatory-documents/analyze", summary="触发 AI 分析")
async def trigger_ai_analysis(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """触发 AI 分析未处理的文档"""
    stats = await analyze_new_documents(db, limit=limit)
    return {"code": 200, "message": "success", "data": stats}


@router.post("/regulatory-documents/{doc_id}/analyze", summary="分析单个文档")
async def analyze_single_document(doc_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """对单个文档执行 AI 分析"""
    doc = await repo.get_document_by_id(db, doc_id)
    if not doc:
        return {"code": 404, "message": "文档不存在", "data": None}

    success = await analyze_and_update(db, doc)
    return {"code": 200, "message": "success" if success else "failed", "data": {"id": str(doc_id), "analyzed": success}}
