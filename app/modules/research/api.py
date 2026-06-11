"""研发项目 API 路由."""

import uuid
from fastapi import APIRouter, Depends, Query, UploadFile, File, Body
from fastapi.responses import JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import CurrentUser
from app.core.response import paginated_response, success_response, error_response
from app.modules.research import service
from app.modules.research.schemas import (
    ResearchProjectCreate,
    ResearchProjectResponse,
    ResearchProjectUpdate,
)
from app.shared.module_api import create_module_router
from app.shared.module_registry import MODULES_BY_CODE

router = create_module_router(MODULES_BY_CODE["research"])


@router.post("/projects", summary="创建研发项目")
async def create_project(
    data: ResearchProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    # Route to bayesian_projects if project_type=bayesian
    if data.project_type == "bayesian":
        project = await service.create_bayesian_project(db, {
            "name": data.name,
            "description": data.description,
            "status": "draft",
        })
        return success_response(data={
            "id": str(project.id),
            "name": project.name,
            "description": project.description,
            "status": project.status,
            "created_at": project.created_at.isoformat(),
        })
    
    project = await service.create_project(db, data)
    return success_response(data=ResearchProjectResponse.model_validate(project))


@router.get("/projects", summary="获取研发项目列表")
async def get_projects(
    stage: str | None = Query(None, description="项目阶段"),
    status: str | None = Query(None, description="项目状态"),
    keyword: str | None = Query(None, description="搜索项目编号或名称"),
    project_type: str | None = Query(None, description="项目类型过滤"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    # Route to bayesian_projects if project_type=bayesian
    if project_type == "bayesian":
        projects, total = await service.get_bayesian_projects(
            db, keyword=keyword, page=page, page_size=page_size
        )
        return paginated_response(
            data=[{
                "id": str(p.id),
                "name": p.name,
                "description": p.description,
                "status": p.status,
                "created_at": p.created_at.isoformat(),
                "updated_at": p.updated_at.isoformat() if p.updated_at else None,
            } for p in projects],
            page=page,
            page_size=page_size,
            total=total,
        )
    
    projects, total = await service.get_projects(
        db, stage=stage, status=status, keyword=keyword, project_type=project_type,
        page=page, page_size=page_size
    )
    return paginated_response(
        data=[ResearchProjectResponse.model_validate(p) for p in projects],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/projects/{project_id}", summary="获取研发项目详情")
async def get_project(
    project_id: uuid.UUID,
    project_type: str | None = Query(None, description="项目类型"),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    # Route to bayesian_projects if project_type=bayesian
    if project_type == "bayesian":
        project = await service.get_bayesian_project(db, project_id)
        components = await service.get_components(db, project_id)
        objectives = await service.get_objectives(db, project_id)
        experiments = await service.get_experiments(db, project_id)
        
        return success_response(data={
            "id": str(project.id),
            "name": project.name,
            "description": project.description,
            "status": project.status,
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat() if project.updated_at else None,
            "components": [
                {
                    "id": str(c.id),
                    "project_id": str(c.project_id),
                    "name": c.name,
                    "component_type": c.component_type,
                    "lower_bound": c.lower_bound,
                    "upper_bound": c.upper_bound,
                    "data_points": c.data_points,
                    "categorical_values": c.categorical_values,
                    "created_at": c.created_at.isoformat(),
                } for c in components
            ],
            "objectives": [
                {
                    "id": str(o.id),
                    "project_id": str(o.project_id),
                    "name": o.name,
                    "direction": o.direction,
                    "threshold": o.threshold,
                    "created_at": o.created_at.isoformat(),
                } for o in objectives
            ],
            "experiments": [
                {
                    "id": str(e.id),
                    "project_id": str(e.project_id),
                    "batch_number": e.batch_number,
                    "parameters": e.parameters,
                    "results": e.results,
                    "is_suggested": e.is_suggested,
                    "status": e.status,
                    "created_at": e.created_at.isoformat(),
                } for e in experiments
            ],
        })
    
    project = await service.get_project(db, project_id)
    return success_response(data=ResearchProjectResponse.model_validate(project))


@router.put("/projects/{project_id}", summary="更新研发项目")
async def update_project(
    project_id: uuid.UUID,
    data: ResearchProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    project = await service.update_project(db, project_id, data)
    return success_response(data=ResearchProjectResponse.model_validate(project))


@router.delete("/projects/{project_id}", summary="删除研发项目")
async def delete_project(
    project_id: uuid.UUID,
    project_type: str | None = Query(None, description="项目类型"),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    # Route to bayesian_projects if project_type=bayesian
    if project_type == "bayesian":
        await service.delete_bayesian_project(db, project_id)
    else:
        await service.delete_project(db, project_id)
    return success_response(message="删除成功")


# ============ ICH Q3C/Q3D 杂质识别 APIs ============

@router.post("/ich/q3c/analyze", summary="ICH Q3C 溶剂残留分析")
async def analyze_ich_q3c(
    file: UploadFile = File(...),
    current_user: CurrentUser = None,
) -> JSONResponse:
    """上传 DOCX 文件进行 ICH Q3C 溶剂残留分析"""
    from app.modules.research import ich_service
    
    if not file.filename.endswith('.docx'):
        return error_response(message="只支持 DOCX 格式文件")
    
    content = await file.read()
    result = await ich_service.analyze_ich_q3c_with_llm(content)
    
    return success_response(data=result)


# ============ LLM 配置管理 APIs ============

@router.get("/llm/config", summary="获取 LLM 配置")
async def get_llm_config(current_user: CurrentUser = None) -> JSONResponse:
    """获取当前 LLM 配置"""
    from app.modules.research.llm_service import llm_config
    return success_response(data=llm_config.get_config())


@router.put("/llm/config", summary="更新 LLM 配置")
async def update_llm_config(
    api_key: str = Body(None, description="API Key"),
    base_url: str = Body(None, description="API Base URL"),
    model: str = Body(None, description="模型名称"),
    current_user: CurrentUser = None,
) -> JSONResponse:
    """更新 LLM 配置"""
    from app.modules.research.llm_service import llm_config
    
    llm_config.update_config(api_key=api_key, base_url=base_url, model=model)
    
    return success_response(
        data=llm_config.get_config(),
        message="配置已更新"
    )


@router.post("/llm/test", summary="测试 LLM 连接")
async def test_llm_connection(current_user: CurrentUser = None) -> JSONResponse:
    """测试 LLM 连接"""
    from app.modules.research.llm_service import llm_config
    
    result = await llm_config.test_connection()
    
    if result["success"]:
        return success_response(data=result)
    else:
        return error_response(message=result["message"])


@router.post("/ich/analyze", summary="ICH Q3C/Q3D 联合分析")
async def analyze_ich_combined(
    file: UploadFile = File(...),
    route: str = Query(default=None, description="deprecated"),
    use_llm: bool = Query(default=None, description="deprecated"),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    """上传 DOCX 文件，同时进行 ICH Q3C 和 Q3D 分析并持久化"""
    from app.modules.research import ich_service
    from app.modules.research.models import ICHAnalysisRecord
    
    if not file.filename.endswith('.docx'):
        return error_response(message="只支持 DOCX 格式文件")
    
    file_content = await file.read()
    
    try:
        q3d_result = await ich_service.analyze_ich_q3d_with_llm(file_content)
        q3c_result = await ich_service.analyze_ich_q3c_with_llm(file_content)
        
        # 持久化分析记录
        record = ICHAnalysisRecord(
            filename=file.filename,
            q3c_result=q3c_result,
            q3d_result=q3d_result,
            llm_used=True,
            created_by=current_user.id if current_user else None,
        )
        db.add(record)
        await db.flush()
        await db.commit()
        await db.refresh(record)
        
        combined_result = {
            "id": str(record.id),
            "q3d": q3d_result,
            "q3c": q3c_result,
        }
        
        return success_response(data=combined_result)
    except Exception as e:
        await db.rollback()
        return error_response(message=f"分析失败: {str(e)}")


# ============ ICH 分析记录 APIs ============

@router.get("/ich/records", summary="获取 ICH 分析记录列表")
async def get_ich_records(
    keyword: str | None = Query(None, description="搜索文件名"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """获取历史 ICH 分析记录列表"""
    from app.modules.research.models import ICHAnalysisRecord
    from sqlalchemy import select, func
    
    query = select(ICHAnalysisRecord).where(ICHAnalysisRecord.is_deleted == False)
    count_query = select(func.count()).select_from(ICHAnalysisRecord).where(ICHAnalysisRecord.is_deleted == False)
    
    if keyword:
        pattern = f"%{keyword}%"
        query = query.where(ICHAnalysisRecord.filename.ilike(pattern))
        count_query = count_query.where(ICHAnalysisRecord.filename.ilike(pattern))
    
    total = (await db.execute(count_query)).scalar_one()
    query = query.order_by(ICHAnalysisRecord.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    records = result.scalars().all()
    
    items = []
    for r in records:
        items.append({
            "id": str(r.id),
            "filename": r.filename,
            "route": r.route,
            "llm_used": r.llm_used,
            "q3c_total": r.q3c_result.get("total_solvents", 0) if r.q3c_result else 0,
            "q3d_total": r.q3d_result.get("total_elements", 0) if r.q3d_result else 0,
            "q3d_needs_assessment": r.q3d_result.get("needs_assessment", 0) if r.q3d_result else 0,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })
    
    return paginated_response(data=items, page=page, page_size=page_size, total=total)


@router.get("/ich/records/{record_id}", summary="获取 ICH 分析记录详情")
async def get_ich_record(
    record_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """获取单个 ICH 分析记录的完整结果"""
    from app.modules.research.models import ICHAnalysisRecord
    from sqlalchemy import select
    
    result = await db.execute(
        select(ICHAnalysisRecord).where(
            ICHAnalysisRecord.id == record_id,
            ICHAnalysisRecord.is_deleted == False,
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        return error_response(message="记录不存在")
    
    return success_response(data={
        "id": str(record.id),
        "filename": record.filename,
        "route": record.route,
        "llm_used": record.llm_used,
        "notes": record.notes,
        "q3c": record.q3c_result,
        "q3d": record.q3d_result,
        "created_at": record.created_at.isoformat() if record.created_at else None,
    })


@router.delete("/ich/records/{record_id}", summary="删除 ICH 分析记录")
async def delete_ich_record(
    record_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    """软删除 ICH 分析记录"""
    from app.modules.research.models import ICHAnalysisRecord
    from sqlalchemy import select
    
    result = await db.execute(
        select(ICHAnalysisRecord).where(
            ICHAnalysisRecord.id == record_id,
            ICHAnalysisRecord.is_deleted == False,
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        return error_response(message="记录不存在")
    
    record.is_deleted = True
    await db.flush()
    await db.commit()
    
    return success_response(message="删除成功")


# ============ Bayesian Optimization APIs ============

@router.post("/projects/{project_id}/components", summary="添加贝叶斯优化参数")
async def add_component(
    project_id: uuid.UUID,
    data: dict = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    component = await service.create_component(db, project_id, data)
    return success_response(data={"id": str(component.id), **data})


@router.get("/projects/{project_id}/components", summary="获取项目参数列表")
async def get_components(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    components = await service.get_components(db, project_id)
    return success_response(data=components)


@router.delete("/components/{component_id}", summary="删除参数")
async def delete_component(
    component_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    await service.delete_component(db, component_id)
    return success_response(message="参数已删除")


@router.post("/projects/{project_id}/objectives", summary="添加优化目标")
async def add_objective(
    project_id: uuid.UUID,
    data: dict = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    objective = await service.create_objective(db, project_id, data)
    return success_response(data={"id": str(objective.id), **data})


@router.get("/projects/{project_id}/objectives", summary="获取优化目标列表")
async def get_objectives(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    objectives = await service.get_objectives(db, project_id)
    return success_response(data=objectives)


@router.delete("/objectives/{objective_id}", summary="删除优化目标")
async def delete_objective(
    objective_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    await service.delete_objective(db, objective_id)
    return success_response(message="目标已删除")


@router.get("/projects/{project_id}/experiments", summary="获取实验列表")
async def get_experiments(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    experiments = await service.get_experiments(db, project_id)
    return success_response(data=experiments)


@router.post("/experiments/{experiment_id}/result", summary="记录实验结果")
async def record_result(
    experiment_id: uuid.UUID,
    data: dict = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    experiment = await service.record_experiment_result(db, experiment_id, data)
    return success_response(data=experiment)


@router.post("/projects/{project_id}/suggest", summary="推荐实验")
async def suggest_experiments(
    project_id: uuid.UUID,
    data: dict = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    from app.modules.research.edbo_service import suggest_experiments as edbo_suggest
    batch_size = data.get("batch_size", 5)
    experiments = await edbo_suggest(db, project_id, batch_size)
    return success_response(data=experiments)
