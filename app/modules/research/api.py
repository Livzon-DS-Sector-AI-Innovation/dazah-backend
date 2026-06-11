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


# ============ ICH Q3C/Q3D 杂质识别 APIs ============
@router.post("/ich/q3d/analyze", summary="ICH Q3D 元素杂质分析")
async def analyze_ich_q3d(
    file: UploadFile = File(...),
    route: str = Query(default="oral", description="给药途径: oral/parenteral/inhalation/cutaneous"),
    use_llm: bool = Query(default=False, description="是否使用 LLM 增强识别"),
    current_user: CurrentUser = None,
) -> JSONResponse:
    """上传 DOCX 文件进行 ICH Q3D 元素杂质分析"""
    from app.modules.research import ich_service
    
    if not file.filename.endswith('.docx'):
        return error_response(message="只支持 DOCX 格式文件")
    
    if route not in ["oral", "parenteral", "inhalation", "cutaneous"]:
        return error_response(message="无效的给药途径，可选: oral/parenteral/inhalation/cutaneous")
    
    content = await file.read()
    
    if use_llm:
        result = await ich_service.analyze_ich_q3d_with_llm(content, route=route)
    else:
        result = ich_service.analyze_ich_q3d(content, route=route)
    
    return success_response(data=result)


@router.post("/ich/q3c/analyze", summary="ICH Q3C 溶剂残留分析")
async def analyze_ich_q3c(
    file: UploadFile = File(...),
    use_llm: bool = Query(default=False, description="是否使用 LLM 增强识别"),
    current_user: CurrentUser = None,
) -> JSONResponse:
    """上传 DOCX 文件进行 ICH Q3C 溶剂残留分析"""
    from app.modules.research import ich_service
    
    if not file.filename.endswith('.docx'):
        return error_response(message="只支持 DOCX 格式文件")
    
    content = await file.read()
    
    if use_llm:
        result = await ich_service.analyze_ich_q3c_with_llm(content)
    else:
        result = ich_service.analyze_ich_q3c(content)
    
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
