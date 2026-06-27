"""研发项目管理 API"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import CurrentUser
from app.modules.rd_project import service
from app.modules.rd_project.schemas import (
    RdProjectCreate, RdProjectUpdate, RdProjectResponse,
    RdMilestoneCreate, RdMilestoneUpdate, RdMilestoneResponse,
    RdStageRecordCreate, RdStageRecordUpdate, RdStageRecordResponse,
    RdResearchTrackCreate, RdResearchTrackUpdate, RdResearchTrackResponse,
    RdResearchFindingCreate, RdResearchFindingUpdate, RdResearchFindingResponse
)

router = APIRouter(prefix="/projects", tags=["研发项目管理"])


# ===== Project Endpoints =====

@router.post("", response_model=RdProjectResponse, summary="创建研发项目")
async def create_project(
    data: RdProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    user_id = current_user.id if current_user else None
    return await service.create_project(db, data, user_id)


@router.get("", response_model=list[RdProjectResponse], summary="获取项目列表")
async def get_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    current_stage: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    projects, total = await service.get_projects(
        db, skip, limit, status, current_stage, priority, keyword
    )
    return projects


@router.get("/{project_id}", response_model=RdProjectResponse, summary="获取项目详情")
async def get_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    return await service.get_project(db, project_id)


@router.put("/{project_id}", response_model=RdProjectResponse, summary="更新项目")
async def update_project(
    project_id: UUID,
    data: RdProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    user_id = current_user.id if current_user else None
    return await service.update_project(db, project_id, data, user_id)


@router.delete("/{project_id}", summary="删除项目")
async def delete_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    await service.delete_project(db, project_id)
    return {"message": "项目已删除"}


# ===== Milestone Endpoints =====

@router.post("/{project_id}/milestones", response_model=RdMilestoneResponse, summary="创建里程碑")
async def create_milestone(
    project_id: UUID,
    data: RdMilestoneCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    user_id = current_user.id if current_user else None
    return await service.create_milestone(db, project_id, data, user_id)


@router.get("/{project_id}/milestones", response_model=list[RdMilestoneResponse], summary="获取里程碑列表")
async def get_milestones(
    project_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    return await service.get_milestones(db, project_id)


@router.put("/milestones/{milestone_id}", response_model=RdMilestoneResponse, summary="更新里程碑")
async def update_milestone(
    milestone_id: UUID,
    data: RdMilestoneUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    user_id = current_user.id if current_user else None
    return await service.update_milestone(db, milestone_id, data, user_id)


# ===== Stage Record Endpoints =====

@router.post("/{project_id}/stages", response_model=RdStageRecordResponse, summary="创建阶段记录")
async def create_stage_record(
    project_id: UUID,
    data: RdStageRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    user_id = current_user.id if current_user else None
    return await service.create_stage_record(db, project_id, data, user_id)


@router.get("/{project_id}/stages", response_model=list[RdStageRecordResponse], summary="获取阶段记录列表")
async def get_stage_records(
    project_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    return await service.get_stage_records(db, project_id)


@router.put("/stages/{record_id}", response_model=RdStageRecordResponse, summary="更新阶段记录")
async def update_stage_record(
    record_id: UUID,
    data: RdStageRecordUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    user_id = current_user.id if current_user else None
    return await service.update_stage_record(db, record_id, data, user_id)


# ===== Research Track Endpoints =====

@router.post("/{project_id}/tracks", response_model=RdResearchTrackResponse, summary="创建研究项")
async def create_research_track(
    project_id: UUID,
    data: RdResearchTrackCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    user_id = current_user.id if current_user else None
    return await service.create_research_track(db, project_id, data, user_id)


@router.get("/{project_id}/tracks", response_model=list[RdResearchTrackResponse], summary="获取研究项列表")
async def get_research_tracks(
    project_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    return await service.get_research_tracks(db, project_id)


@router.put("/tracks/{track_id}", response_model=RdResearchTrackResponse, summary="更新研究项")
async def update_research_track(
    track_id: UUID,
    data: RdResearchTrackUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    user_id = current_user.id if current_user else None
    return await service.update_research_track(db, track_id, data, user_id)


# ===== Research Finding Endpoints =====

@router.post("/tracks/{track_id}/findings", response_model=RdResearchFindingResponse, summary="创建研究发现")
async def create_research_finding(
    track_id: UUID,
    data: RdResearchFindingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    user_id = current_user.id if current_user else None
    return await service.create_research_finding(db, track_id, data, user_id)


@router.get("/tracks/{track_id}/findings", response_model=list[RdResearchFindingResponse], summary="获取研究发现列表")
async def get_research_findings(
    track_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    return await service.get_research_findings(db, track_id)


@router.put("/findings/{finding_id}", response_model=RdResearchFindingResponse, summary="更新研究发现")
async def update_research_finding(
    finding_id: UUID,
    data: RdResearchFindingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    user_id = current_user.id if current_user else None
    return await service.update_research_finding(db, finding_id, data, user_id)


# ===== Conclusion Version Endpoints =====

@router.post("/tracks/{track_id}/conclusions", summary="发布新结论版本")
async def publish_conclusion_version(
    track_id: UUID,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    """发布新的结论版本，更新研究项的当前结论"""
    user_id = current_user.id if current_user else None
    conclusion = data.get("conclusion", "")
    confidence = data.get("confidence", "preliminary")
    return await service.publish_conclusion_version(db, track_id, conclusion, confidence, user_id)


@router.get("/tracks/{track_id}/conclusions", summary="获取结论历史")
async def get_conclusion_history(
    track_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """获取研究项的结论版本历史"""
    return await service.get_conclusion_history(db, track_id)
