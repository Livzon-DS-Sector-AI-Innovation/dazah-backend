"""研发项目 API 路由."""

import uuid

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import CurrentUser
from app.core.response import paginated_response, success_response
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
    project = await service.create_project(db, data)
    return success_response(data=ResearchProjectResponse.model_validate(project))


@router.get("/projects", summary="获取研发项目列表")
async def get_projects(
    stage: str | None = Query(None, description="项目阶段"),
    status: str | None = Query(None, description="项目状态"),
    keyword: str | None = Query(None, description="搜索项目编号或名称"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    projects, total = await service.get_projects(
        db, stage=stage, status=status, keyword=keyword, page=page, page_size=page_size
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
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
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
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    await service.delete_project(db, project_id)
    return success_response(message="删除成功")
