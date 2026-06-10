"""Research API routes for Bayesian optimization."""

import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Query
from fastapi.responses import JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import CurrentUser
from app.core.response import success_response
from app.modules.research import service
from app.modules.research.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectDetail,
    ComponentCreate,
    ComponentResponse,
    ObjectiveCreate,
    ObjectiveResponse,
    ExperimentSuggest,
    ExperimentResponse,
    ReactionScopeCreate,
    ReactionScopeResponse,
    CSVImportResponse,
)

router = APIRouter()


# ============ Project APIs ============
@router.post("/projects", summary="创建贝叶斯优化项目")
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    """创建贝叶斯优化项目，可同时定义组件和目标"""
    project = await service.create_project(db, data)
    return success_response(data=ProjectDetail.model_validate(project))


@router.get("/projects", summary="获取项目列表")
async def get_projects(
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """获取所有贝叶斯优化项目"""
    projects = await service.get_projects(db)
    return success_response(data=[ProjectResponse.model_validate(p) for p in projects])


@router.get("/projects/{project_id}", summary="获取项目详情")
async def get_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """获取项目详情，包含组件和目标"""
    project = await service.get_project(db, project_id)
    return success_response(data=ProjectDetail.model_validate(project))


@router.put("/projects/{project_id}", summary="更新项目")
async def update_project(
    project_id: uuid.UUID,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    """更新项目基本信息"""
    project = await service.update_project(db, project_id, data)
    return success_response(data=ProjectResponse.model_validate(project))


@router.delete("/projects/{project_id}", summary="删除项目")
async def delete_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    """删除项目"""
    await service.delete_project(db, project_id)
    return success_response(message="删除成功")


# ============ Component APIs ============
@router.post("/projects/{project_id}/components", summary="添加组件")
async def add_component(
    project_id: uuid.UUID,
    data: ComponentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    """添加反应组件"""
    component = await service.add_component(db, project_id, data)
    return success_response(data=ComponentResponse.model_validate(component))


@router.get("/projects/{project_id}/components", summary="获取组件列表")
async def get_components(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """获取项目的所有组件"""
    components = await service.get_components(db, project_id)
    return success_response(data=[ComponentResponse.model_validate(c) for c in components])


# ============ Objective APIs ============
@router.post("/projects/{project_id}/objectives", summary="添加目标")
async def add_objective(
    project_id: uuid.UUID,
    data: ObjectiveCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    """添加优化目标"""
    objective = await service.add_objective(db, project_id, data)
    return success_response(data=ObjectiveResponse.model_validate(objective))


@router.get("/projects/{project_id}/objectives", summary="获取目标列表")
async def get_objectives(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """获取项目的所有优化目标"""
    objectives = await service.get_objectives(db, project_id)
    return success_response(data=[ObjectiveResponse.model_validate(o) for o in objectives])


# ============ Experiment APIs ============
@router.post("/experiments/suggest", summary="推荐实验")
async def suggest_experiments(
    data: ExperimentSuggest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    """基于贝叶斯优化推荐下一批实验"""
    experiments = await service.suggest_experiments(db, data)
    return success_response(data=[ExperimentResponse.model_validate(e) for e in experiments])


@router.get("/projects/{project_id}/experiments", summary="获取实验列表")
async def get_experiments(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """获取项目的所有实验记录"""
    experiments = await service.get_experiments(db, project_id)
    return success_response(data=[ExperimentResponse.model_validate(e) for e in experiments])


@router.post("/experiments/{experiment_id}/result", summary="记录实验结果")
async def record_result(
    experiment_id: uuid.UUID,
    results: dict,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    """记录实验结果"""
    experiment = await service.record_experiment_result(db, experiment_id, results)
    return success_response(data=ExperimentResponse.model_validate(experiment))


# ============ Reaction Scope APIs ============
@router.post("/projects/{project_id}/reaction-scopes", summary="生成反应范围")
async def generate_reaction_scope(
    project_id: uuid.UUID,
    data: ReactionScopeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    """根据组件定义生成反应范围"""
    scope = await service.generate_reaction_scope(db, project_id, data.name)
    return success_response(data=ReactionScopeResponse.model_validate(scope))


@router.get("/projects/{project_id}/reaction-scopes", summary="获取反应范围列表")
async def get_reaction_scopes(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """获取项目的所有反应范围"""
    scopes = await service.get_reaction_scopes(db, project_id)
    return success_response(data=[ReactionScopeResponse.model_validate(s) for s in scopes])


# ============ CSV Import/Export APIs ============
@router.post("/projects/{project_id}/import-csv", summary="导入 CSV 数据")
async def import_csv(
    project_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    """从 CSV 文件导入实验数据"""
    content = await file.read()
    result = await service.import_csv(db, project_id, content)
    return success_response(data=result)


@router.get("/projects/{project_id}/export-csv", summary="导出 CSV 数据")
async def export_csv(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """导出实验数据为 CSV 文件"""
    csv_bytes = await service.export_csv(db, project_id)
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=experiments_{project_id}.csv"},
    )
