"""研发项目管理 Service"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.rd_project.models import (
    RdProject, RdMilestone, RdStageRecord,
    RdResearchTrack, RdResearchFinding
)
from app.modules.rd_project.schemas import (
    RdProjectCreate, RdProjectUpdate,
    RdMilestoneCreate, RdMilestoneUpdate,
    RdStageRecordCreate, RdStageRecordUpdate,
    RdResearchTrackCreate, RdResearchTrackUpdate,
    RdResearchFindingCreate, RdResearchFindingUpdate
)


# ===== Project Service =====

async def create_project(db: AsyncSession, data: RdProjectCreate, user_id: Optional[UUID] = None) -> RdProject:
    """创建研发项目"""
    project = RdProject(
        **data.model_dump(),
        status="initiation",
        current_stage="initiation",
        overall_progress=0.0,
        created_by=user_id,
        updated_by=user_id
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


async def get_project(db: AsyncSession, project_id: UUID) -> RdProject:
    """获取项目详情"""
    result = await db.execute(
        select(RdProject).where(RdProject.id == project_id, RdProject.is_deleted == False)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project


async def get_projects(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    current_stage: Optional[str] = None,
    priority: Optional[str] = None,
    keyword: Optional[str] = None
) -> tuple[list[RdProject], int]:
    """获取项目列表"""
    query = select(RdProject).where(RdProject.is_deleted == False)
    
    if status:
        query = query.where(RdProject.status == status)
    if current_stage:
        query = query.where(RdProject.current_stage == current_stage)
    if priority:
        query = query.where(RdProject.priority == priority)
    if keyword:
        query = query.where(RdProject.name.ilike(f"%{keyword}%") | RdProject.api_name.ilike(f"%{keyword}%"))
    
    # 总数
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()
    
    # 分页
    query = query.order_by(RdProject.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    projects = result.scalars().all()
    
    return list(projects), total


async def update_project(db: AsyncSession, project_id: UUID, data: RdProjectUpdate, user_id: Optional[UUID] = None) -> RdProject:
    """更新项目"""
    project = await get_project(db, project_id)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    project.updated_by = user_id
    await db.commit()
    await db.refresh(project)
    return project


async def delete_project(db: AsyncSession, project_id: UUID) -> None:
    """删除项目（软删除）"""
    project = await get_project(db, project_id)
    project.is_deleted = True
    await db.commit()


# ===== Milestone Service =====

async def create_milestone(db: AsyncSession, project_id: UUID, data: RdMilestoneCreate, user_id: Optional[UUID] = None) -> RdMilestone:
    """创建里程碑"""
    await get_project(db, project_id)  # 验证项目存在
    milestone = RdMilestone(
        project_id=project_id,
        **data.model_dump(),
        status="planned",
        created_by=user_id,
        updated_by=user_id
    )
    db.add(milestone)
    await db.commit()
    await db.refresh(milestone)
    return milestone


async def get_milestones(db: AsyncSession, project_id: UUID) -> list[RdMilestone]:
    """获取项目的里程碑列表"""
    result = await db.execute(
        select(RdMilestone)
        .where(RdMilestone.project_id == project_id, RdMilestone.is_deleted == False)
        .order_by(RdMilestone.planned_date)
    )
    return list(result.scalars().all())


async def update_milestone(db: AsyncSession, milestone_id: UUID, data: RdMilestoneUpdate, user_id: Optional[UUID] = None) -> RdMilestone:
    """更新里程碑"""
    result = await db.execute(
        select(RdMilestone).where(RdMilestone.id == milestone_id, RdMilestone.is_deleted == False)
    )
    milestone = result.scalar_one_or_none()
    if not milestone:
        raise HTTPException(status_code=404, detail="里程碑不存在")
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(milestone, field, value)
    milestone.updated_by = user_id
    await db.commit()
    await db.refresh(milestone)
    return milestone


# ===== Stage Record Service =====

async def create_stage_record(db: AsyncSession, project_id: UUID, data: RdStageRecordCreate, user_id: Optional[UUID] = None) -> RdStageRecord:
    """创建阶段记录"""
    await get_project(db, project_id)
    record = RdStageRecord(
        project_id=project_id,
        **data.model_dump(),
        status="not_started",
        created_by=user_id,
        updated_by=user_id
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def get_stage_records(db: AsyncSession, project_id: UUID) -> list[RdStageRecord]:
    """获取项目的阶段记录列表"""
    result = await db.execute(
        select(RdStageRecord)
        .where(RdStageRecord.project_id == project_id, RdStageRecord.is_deleted == False)
        .order_by(RdStageRecord.created_at)
    )
    return list(result.scalars().all())


async def update_stage_record(db: AsyncSession, record_id: UUID, data: RdStageRecordUpdate, user_id: Optional[UUID] = None) -> RdStageRecord:
    """更新阶段记录"""
    result = await db.execute(
        select(RdStageRecord).where(RdStageRecord.id == record_id, RdStageRecord.is_deleted == False)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="阶段记录不存在")
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)
    record.updated_by = user_id
    await db.commit()
    await db.refresh(record)
    return record


# ===== Research Track Service =====

async def create_research_track(db: AsyncSession, project_id: UUID, data: RdResearchTrackCreate, user_id: Optional[UUID] = None) -> RdResearchTrack:
    """创建研究项"""
    await get_project(db, project_id)
    track = RdResearchTrack(
        project_id=project_id,
        **data.model_dump(),
        status="active",
        conclusion_version=0,
        created_by=user_id,
        updated_by=user_id
    )
    db.add(track)
    await db.commit()
    await db.refresh(track)
    return track


async def get_research_tracks(db: AsyncSession, project_id: UUID) -> list[RdResearchTrack]:
    """获取项目的研究项列表"""
    result = await db.execute(
        select(RdResearchTrack)
        .where(RdResearchTrack.project_id == project_id, RdResearchTrack.is_deleted == False)
        .order_by(RdResearchTrack.created_at)
    )
    return list(result.scalars().all())


async def update_research_track(db: AsyncSession, track_id: UUID, data: RdResearchTrackUpdate, user_id: Optional[UUID] = None) -> RdResearchTrack:
    """更新研究项"""
    result = await db.execute(
        select(RdResearchTrack).where(RdResearchTrack.id == track_id, RdResearchTrack.is_deleted == False)
    )
    track = result.scalar_one_or_none()
    if not track:
        raise HTTPException(status_code=404, detail="研究项不存在")
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(track, field, value)
    track.updated_by = user_id
    await db.commit()
    await db.refresh(track)
    return track


# ===== Research Finding Service =====

async def create_research_finding(db: AsyncSession, track_id: UUID, data: RdResearchFindingCreate, user_id: Optional[UUID] = None) -> RdResearchFinding:
    """创建研究发现"""
    result = await db.execute(
        select(RdResearchTrack).where(RdResearchTrack.id == track_id, RdResearchTrack.is_deleted == False)
    )
    track = result.scalar_one_or_none()
    if not track:
        raise HTTPException(status_code=404, detail="研究项不存在")
    
    finding = RdResearchFinding(
        track_id=track_id,
        **data.model_dump(),
        version=1,
        created_by=user_id,
        updated_by=user_id
    )
    db.add(finding)
    await db.commit()
    await db.refresh(finding)
    return finding


async def get_research_findings(db: AsyncSession, track_id: UUID) -> list[RdResearchFinding]:
    """获取研究项的发现列表"""
    result = await db.execute(
        select(RdResearchFinding)
        .where(RdResearchFinding.track_id == track_id, RdResearchFinding.is_deleted == False)
        .order_by(RdResearchFinding.created_at)
    )
    return list(result.scalars().all())


async def update_research_finding(db: AsyncSession, finding_id: UUID, data: RdResearchFindingUpdate, user_id: Optional[UUID] = None) -> RdResearchFinding:
    """更新研究发现"""
    result = await db.execute(
        select(RdResearchFinding).where(RdResearchFinding.id == finding_id, RdResearchFinding.is_deleted == False)
    )
    finding = result.scalar_one_or_none()
    if not finding:
        raise HTTPException(status_code=404, detail="研究发现不存在")
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(finding, field, value)
    finding.updated_by = user_id
    await db.commit()
    await db.refresh(finding)
    return finding


# ===== Conclusion Version Service =====

async def publish_conclusion_version(
    db: AsyncSession, 
    track_id: UUID, 
    conclusion: str, 
    confidence: str, 
    user_id: Optional[UUID] = None
) -> dict:
    """发布新的结论版本"""
    result = await db.execute(
        select(RdResearchTrack).where(RdResearchTrack.id == track_id, RdResearchTrack.is_deleted == False)
    )
    track = result.scalar_one_or_none()
    if not track:
        raise HTTPException(status_code=404, detail="研究项不存在")
    
    # Increment version and update current conclusion
    track.conclusion_version = (track.conclusion_version or 0) + 1
    track.current_conclusion = conclusion
    track.conclusion_confidence = confidence
    track.updated_by = user_id
    
    await db.commit()
    await db.refresh(track)
    
    return {
        "version": track.conclusion_version,
        "conclusion": track.current_conclusion,
        "confidence": track.conclusion_confidence,
        "updated_at": track.updated_at.isoformat() if track.updated_at else None
    }


async def get_conclusion_history(db: AsyncSession, track_id: UUID) -> list[dict]:
    """获取研究项的结论版本历史
    
    注意：当前实现只返回当前结论，因为数据库中没有单独的结论历史表。
    如需完整历史，需要创建 rd_track_conclusion_versions 表。
    """
    result = await db.execute(
        select(RdResearchTrack).where(RdResearchTrack.id == track_id, RdResearchTrack.is_deleted == False)
    )
    track = result.scalar_one_or_none()
    if not track:
        raise HTTPException(status_code=404, detail="研究项不存在")
    
    # For now, return only current conclusion
    # In a full implementation, this would query a conclusion_versions table
    if track.current_conclusion:
        return [{
            "version": track.conclusion_version or 1,
            "conclusion": track.current_conclusion,
            "confidence": track.conclusion_confidence,
            "updated_at": track.updated_at.isoformat() if track.updated_at else None,
            "updated_by": str(track.updated_by) if track.updated_by else None
        }]
    return []
