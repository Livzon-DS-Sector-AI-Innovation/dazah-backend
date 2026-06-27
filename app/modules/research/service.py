"""Research business workflows."""

import uuid
from uuid import UUID
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateException, NotFoundException
from app.modules.research import repository as repo
from app.modules.research.models import (
    ResearchProject,
    RdProject, RdMilestone, RdStageRecord, RdResearchTrack, RdResearchFinding,
)
from app.modules.research.schemas import (
    ResearchProjectCreate,
    ResearchProjectUpdate,
    RdProjectCreate, RdProjectUpdate, RdProjectResponse,
    RdMilestoneCreate, RdMilestoneUpdate, RdMilestoneResponse,
    RdStageRecordCreate, RdStageRecordUpdate, RdStageRecordResponse,
    RdResearchTrackCreate, RdResearchTrackUpdate, RdResearchTrackResponse,
    RdResearchFindingCreate, RdResearchFindingUpdate, RdResearchFindingResponse,
)


async def create_project(
    db: AsyncSession, data: ResearchProjectCreate
) -> ResearchProject:
    # Auto-generate project_no if not provided
    project_no = data.project_no
    if not project_no:
        project_no = f"PRJ-{str(uuid.uuid4())[:8].upper()}"
    
    if await repo.exists_by_project_no(db, project_no):
        raise DuplicateException("项目编号", project_no)
    
    project_data = data.model_dump()
    project_data["project_no"] = project_no
    return await repo.create_project(db, project_data)


async def get_project(db: AsyncSession, project_id: uuid.UUID) -> ResearchProject:
    project = await repo.get_project_by_id(db, project_id)
    if not project:
        raise NotFoundException("研发项目", str(project_id))
    return project


async def get_rd_project(db: AsyncSession, project_id: UUID) -> RdProject:
    """获取 RdProject（用于 rd_milestones 等外键验证）"""
    result = await db.execute(
        select(RdProject).where(
            RdProject.id == project_id,
            RdProject.is_deleted == False,
        )
    )
    project = result.scalar_one_or_none()
    if not project:
        raise NotFoundException("研发项目", str(project_id))
    return project


async def get_projects(
    db: AsyncSession,
    stage: str | None = None,
    status: str | None = None,
    keyword: str | None = None,
    project_type: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[ResearchProject], int]:
    return await repo.get_projects(
        db, stage=stage, status=status, keyword=keyword, project_type=project_type,
        page=page, page_size=page_size
    )


async def update_project(
    db: AsyncSession,
    project_id: uuid.UUID,
    data: ResearchProjectUpdate,
) -> ResearchProject:
    project = await get_project(db, project_id)
    update_data = data.model_dump(exclude_unset=True)
    if "project_no" in update_data and update_data["project_no"] != project.project_no:
        if await repo.exists_by_project_no(db, update_data["project_no"], exclude_id=project_id):
            raise DuplicateException("项目编号", update_data["project_no"])
    return await repo.update_project(db, project, update_data)


async def delete_project(db: AsyncSession, project_id: uuid.UUID) -> None:
    project = await get_project(db, project_id)
    await repo.delete_project(db, project)


# ICH Analysis functions
from app.modules.research.models import ICHAnalysisRecord
from sqlalchemy import select, func


async def analyze_ich_q3c(
    db: AsyncSession,
    file_content: bytes,
    filename: str,
    route: str | None = None,
) -> dict:
    """Analyze ICH Q3C solvent residuals from uploaded file."""
    # TODO: Implement actual Q3C analysis logic
    # For now, create a placeholder record
    record = ICHAnalysisRecord(
        filename=filename,
        route=route,
        q3c_result={"status": "pending", "message": "Q3C analysis not yet implemented"},
        q3d_result=None,
        llm_used=False,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    
    return {
        "id": str(record.id),
        "filename": record.filename,
        "route": record.route,
        "q3c_result": record.q3c_result,
        "q3d_result": record.q3d_result,
        "llm_used": record.llm_used,
        "created_at": record.created_at.isoformat() if record.created_at else None,
    }


async def analyze_ich_combined(
    db: AsyncSession,
    file_content: bytes,
    filename: str,
    route: str | None = None,
    use_llm: bool = False,
) -> dict:
    """Analyze ICH Q3C/Q3D combined analysis from uploaded file."""
    # TODO: Implement actual combined analysis logic
    # For now, create a placeholder record
    record = ICHAnalysisRecord(
        filename=filename,
        route=route,
        q3c_result={"status": "pending", "message": "Q3C analysis not yet implemented"},
        q3d_result={"status": "pending", "message": "Q3D analysis not yet implemented"},
        llm_used=use_llm,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    
    return {
        "id": str(record.id),
        "filename": record.filename,
        "route": record.route,
        "q3c_result": record.q3c_result,
        "q3d_result": record.q3d_result,
        "llm_used": record.llm_used,
        "created_at": record.created_at.isoformat() if record.created_at else None,
    }


async def get_ich_records(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[ICHAnalysisRecord], int]:
    """Get paginated ICH analysis records."""
    # Get total count
    count_query = select(func.count()).select_from(ICHAnalysisRecord)
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Get paginated records
    query = (
        select(ICHAnalysisRecord)
        .order_by(ICHAnalysisRecord.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    records = list(result.scalars().all())
    
    return records, total


async def get_ich_record(
    db: AsyncSession,
    record_id: uuid.UUID,
) -> ICHAnalysisRecord:
    """Get single ICH analysis record by ID."""
    query = select(ICHAnalysisRecord).where(ICHAnalysisRecord.id == record_id)
    result = await db.execute(query)
    record = result.scalar_one_or_none()
    
    if not record:
        raise NotFoundException("ICH Q3C/Q3D 杂质识别记录", str(record_id))
    
    return record


async def delete_ich_record(
    db: AsyncSession,
    record_id: uuid.UUID,
) -> None:
    """Delete ICH analysis record by ID."""
    record = await get_ich_record(db, record_id)
    await db.delete(record)
    await db.commit()





# ===== Milestone Service =====

async def create_milestone(db: AsyncSession, project_id: UUID, data: RdMilestoneCreate, user_id: Optional[UUID] = None) -> RdMilestone:
    """创建里程碑"""
    await get_rd_project(db, project_id)  # 验证项目存在
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
