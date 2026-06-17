"""研发项目 API 路由."""

import uuid
from fastapi import APIRouter, Body, Depends, File, HTTPException, Query, UploadFile
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
    project_type: str | None = Query(None, description="项目类型过滤"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
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
    return success_response(data={"message": "项目已删除"})


@router.post("/ich/q3c/analyze", summary="ICH Q3C 溶剂残留分析")
async def analyze_ich_q3c(
    file: UploadFile = File(...),
    route: str = Query("oral", description="给药途径"),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    result = await service.analyze_ich_q3c(db, file, route)
    return success_response(data=result)


@router.get("/llm/config", summary="获取 LLM 配置")
async def get_llm_config(current_user: CurrentUser = None) -> JSONResponse:
    config = await service.get_llm_config()
    return success_response(data=config)


@router.put("/llm/config", summary="更新 LLM 配置")
async def update_llm_config(
    data: dict = Body(...),
    current_user: CurrentUser = None,
) -> JSONResponse:
    config = await service.update_llm_config(data)
    return success_response(data=config)


@router.post("/llm/test", summary="测试 LLM 连接")
async def test_llm_connection(current_user: CurrentUser = None) -> JSONResponse:
    result = await service.test_llm_connection()
    return success_response(data=result)


@router.post("/ich/analyze", summary="ICH Q3C/Q3D 联合分析")
async def analyze_ich_combined(
    file: UploadFile = File(...),
    route: str = Query("oral", description="给药途径"),
    use_llm: bool = Query(False, description="是否使用 LLM 增强"),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    result = await service.analyze_ich_combined(db, file, route, use_llm)
    return success_response(data=result)


@router.get("/ich/records", summary="获取 ICH Q3C/Q3D 杂质识别记录列表")
async def get_ich_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    records, total = await service.get_ich_records(db, page=page, page_size=page_size)
    return paginated_response(
        data=[
            {
                "id": str(r.id),
                "filename": r.filename,
                "route": r.route,
                "q3c_result": r.q3c_result,
                "q3d_result": r.q3d_result,
                "llm_used": r.llm_used,
                "notes": r.notes,
                "created_at": r.created_at.isoformat(),
            }
            for r in records
        ],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/ich/records/{record_id}", summary="获取 ICH Q3C/Q3D 杂质识别记录详情")
async def get_ich_record(
    record_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    record = await service.get_ich_record(db, record_id)
    return success_response(
        data={
            "id": str(record.id),
            "filename": record.filename,
            "route": record.route,
            "q3c_result": record.q3c_result,
            "q3d_result": record.q3d_result,
            "llm_used": record.llm_used,
            "notes": record.notes,
            "created_at": record.created_at.isoformat(),
        }
    )


@router.delete("/ich/records/{record_id}", summary="删除 ICH Q3C/Q3D 杂质识别记录")
async def delete_ich_record(
    record_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    await service.delete_ich_record(db, record_id)
    return success_response(data={"message": "记录已删除"})


@router.post("/edbo/optimize", summary="EDBO+ 贝叶斯优化")
async def edbo_optimize(
    file: UploadFile = File(..., description="反应范围 CSV 文件"),
    objectives: str = Body(..., description="目标列名，逗号分隔"),
    objective_modes: str = Body("max", description="目标方向，逗号分隔（max/min）"),
    batch_size: int = Body(5, ge=1, le=100, description="建议实验数量"),
    save_prediction: bool = Body(False, description="是否保存预测文件"),
    current_user: CurrentUser = None,
) -> JSONResponse:
    """
    使用 EDBO+ 进行贝叶斯反应优化。

    上传 CSV 文件（反应范围），指定目标列和优化方向，返回建议的实验列表。
    如果 save_prediction=True，还会返回预测文件（包含所有实验的模型预测结果）。
    """
    from app.modules.research.edbo_runner import run_edbo_optimization
    from app.modules.research.schemas import EDBOOptimizeResponse

    # Parse comma-separated strings
    obj_list = [o.strip() for o in objectives.split(",") if o.strip()]
    mode_list = [m.strip() for m in objective_modes.split(",") if m.strip()]

    if len(obj_list) != len(mode_list):
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail=f"objectives ({len(obj_list)}) and objective_modes ({len(mode_list)}) must have the same length"
        )

    # Read CSV content
    csv_content = (await file.read()).decode("utf-8")

    # Run EDBO+ optimization
    try:
        result = await run_edbo_optimization(
            csv_content=csv_content,
            objectives=obj_list,
            objective_modes=mode_list,
            batch_size=batch_size,
            save_prediction=save_prediction,
        )
    except RuntimeError as e:
        from app.core.response import error_response
        return error_response(message=str(e))

    return success_response(data=EDBOOptimizeResponse(**result))


@router.post("/edbo/generate-scope", summary="生成反应范围")
async def edbo_generate_scope(
    components: dict = Body(..., description="组件定义，支持两种格式：1) 直接值列表 {name: [v1,v2,...]} 2) 范围定义 {name: {type: 'numeric', lower: x, upper: y, data_points: n}} 或 {name: {type: 'categorical', values: [...]}}"),
    objectives: list[str] = Body(default=[], description="优化目标名称列表，会作为新列添加到结果CSV中，初始值为PENDING"),
    batch_size: int = Body(default=5, ge=1, le=100, description="通量大小，表示同时进行的实验数量")
):
    """
    生成反应范围 CSV（所有组合的笛卡尔积）
    
    支持两种组件格式：
    
    1. 简单值列表（直接枚举）:
    ```json
    {
        "solvent": ["THF", "DMSO"],
        "catalyst": ["Pd", "Ni"]
    }
    ```
    
    2. 范围定义（数值型自动生成等间隔值）:
    ```json
    {
        "temperature": {"type": "numeric", "lower": 30, "upper": 90, "data_points": 4},
        "solvent": {"type": "categorical", "values": ["THF", "DMSO", "MeOH"]}
    }
    ```
    
    数值型组件会自动处理有效数字，避免浮点精度问题。
    """
    import itertools
    import math
    import pandas as pd
    from fastapi.responses import StreamingResponse
    import io
    import logging
    
    logger = logging.getLogger(__name__)
    logger.info(f"generate-scope called with objectives: {objectives}")
    logger.info(f"generate-scope components: {components}")
    logger.info(f"generate-scope batch_size: {batch_size}")
    
    def count_significant_digits(num):
        """Count the number of significant digits in a number."""
        if num == 0:
            return 1
        num_str = str(num).lower()
        if 'e' in num_str:
            mantissa = num_str.split('e')[0].replace('.', '').lstrip('0')
            return len(mantissa)
        if '.' in num_str:
            integer_part, decimal_part = num_str.split('.')
            integer_part = integer_part.lstrip('0')
            if integer_part:
                return len(integer_part) + len(decimal_part)
            else:
                decimal_part = decimal_part.lstrip('0')
                return len(decimal_part)
        else:
            return len(num_str.lstrip('0'))
    
    def round_to_significant_digits(num, sig_digits):
        """Round a number to the specified number of significant digits."""
        if num == 0:
            return 0
        if abs(num) == float('inf') or math.isnan(num):
            return num
        magnitude = 10 ** (sig_digits - 1 - int(math.floor(math.log10(abs(num)))))
        rounded = round(num * magnitude) / magnitude
        return rounded
    
    def generate_numeric_values(lower, upper, data_points):
        """Generate numeric values with proper significant digit handling."""
        if lower > upper:
            raise ValueError(f"下限 ({lower}) 不能大于上限 ({upper})")
        if data_points <= 1:
            raise ValueError(f"数据点数必须大于 1")
        
        values = []
        if data_points == 2:
            return [lower, upper]
        
        interval = (upper - lower) / (data_points - 1)
        
        # Check for extreme case: too many data points for small intervals
        if abs(lower) > 1e-15:
            relative_interval = interval / abs(lower)
            if relative_interval < 1e-6:
                raise ValueError(f"数据点过多，间隔过小")
        
        # Determine significant digits
        lower_sig_digits = count_significant_digits(lower)
        upper_sig_digits = count_significant_digits(upper)
        target_sig_digits = min(lower_sig_digits, upper_sig_digits)
        
        # Check if first in-between value rounds to lower limit
        first_in_between = lower + interval
        rounded_first = round_to_significant_digits(first_in_between, target_sig_digits)
        if abs(rounded_first - lower) < 1e-10:
            # Increase significant digits until different
            current_sig_digits = target_sig_digits + 1
            while current_sig_digits <= 15:
                rounded_first = round_to_significant_digits(first_in_between, current_sig_digits)
                if abs(rounded_first - lower) > 1e-10:
                    target_sig_digits = current_sig_digits
                    break
                current_sig_digits += 1
        
        # Generate all values
        for i in range(data_points):
            exact_value = lower + i * interval
            if abs(exact_value) == float('inf') or math.isnan(exact_value):
                values.append(exact_value)
            else:
                rounded_value = round_to_significant_digits(exact_value, target_sig_digits)
                values.append(rounded_value)
        
        return values
    
    # Validate input
    if not components:
        raise HTTPException(status_code=400, detail="组件定义不能为空")
    
    # Process each component
    processed_components = {}
    for key, value in components.items():
        if isinstance(value, list):
            # Simple list format
            processed_components[key] = value
        elif isinstance(value, dict):
            # Range definition format
            comp_type = value.get('type', 'categorical')
            if comp_type == 'numeric':
                lower = value.get('lower')
                upper = value.get('upper')
                data_points = value.get('data_points')
                if lower is None or upper is None or data_points is None:
                    raise HTTPException(
                        status_code=400,
                        detail=f"组件 '{key}' 缺少必要参数 (lower, upper, data_points)"
                    )
                try:
                    processed_components[key] = generate_numeric_values(
                        float(lower), float(upper), int(data_points)
                    )
                except ValueError as e:
                    raise HTTPException(status_code=400, detail=f"组件 '{key}': {str(e)}")
            elif comp_type == 'categorical':
                cat_values = value.get('values', [])
                if not cat_values:
                    raise HTTPException(
                        status_code=400,
                        detail=f"组件 '{key}' 的值列表不能为空"
                    )
                processed_components[key] = cat_values
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"组件 '{key}' 的类型无效: {comp_type}"
                )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"组件 '{key}' 的格式无效"
            )
    
    # Calculate total combinations
    n_combinations = 1
    for key, values in processed_components.items():
        n_combinations *= len(values)
    
    if n_combinations > 10000:
        raise HTTPException(
            status_code=400,
            detail=f"组合数量过大 ({n_combinations})，请减少组件选项"
        )
    
    # Generate Cartesian product
    keys = list(processed_components.keys())
    values = [processed_components[key] for key in keys]
    
    scope = [dict(zip(keys, combination)) for combination in itertools.product(*values)]
    df_scope = pd.DataFrame(scope)
    
    # Convert to CSV (without objective columns - EDBO+ will add them)
    csv_buffer = io.StringIO()
    df_scope.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    scope_csv = csv_buffer.getvalue()
    
    # If objectives are defined, run EDBO+ to get initial sampling recommendations
    # IMPORTANT: Do NOT add objective columns with PENDING values before calling EDBO+.
    # EDBO+ detects missing objective columns and performs initial sampling automatically.
    # If we add PENDING columns first, EDBO+ thinks the scope already exists and refuses to run.
    logger.info(f"Checking objectives: {objectives}, length: {len(objectives)}")
    if objectives:
        logger.info(f"Objectives found, calling EDBO+ for initial sampling with: {objectives}")
        try:
            from app.modules.research.edbo_runner import run_edbo_optimization
            objective_modes = ['max'] * len(objectives)
            
            result = await run_edbo_optimization(
                csv_content=scope_csv,
                objectives=objectives,
                objective_modes=objective_modes,
                batch_size=batch_size,
                save_prediction=False,
            )
            
            result_csv = result.get("csv_data", scope_csv)
            return {
                "csv_data": result_csv,
                "row_count": len(scope),
                "columns": keys + objectives + ["priority"],
                "recommended_experiments": result_csv,
                "optimization_completed": True
            }
        except Exception as e:
            logger.error(f"EDBO+ optimization failed: {e}")
            # Add PENDING objective columns for the fallback response
            for obj in objectives:
                df_scope[obj] = "PENDING"
            csv_buffer = io.StringIO()
            df_scope.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            scope_csv_with_pending = csv_buffer.getvalue()
            
            return {
                "csv_data": scope_csv_with_pending,
                "row_count": len(scope),
                "columns": keys + objectives,
                "optimization_completed": False,
                "optimization_error": str(e)
            }
    
    return {
        "csv_data": scope_csv,
        "row_count": len(scope),
        "columns": keys,
        "optimization_completed": False
    }


# ===== Pilot Workflow API =====

import os
import uuid as uuid_module

from app.modules.research import repository as pilot_repo
from app.modules.research.pilot_workflow.engine import (
    start_workflow as start_workflow_engine,
    approve_step as approve_step_engine,
)
from app.modules.research.schemas import (
    PilotWorkflowCreate,
    PilotWorkflowListResponse,
    PilotWorkflowResponse,
    PilotWorkflowStepResponse,
)


@router.post("/pilot/workflow", summary="创建中试研究")
async def create_pilot_workflow(
    data: PilotWorkflowCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    workflow_data = data.model_dump()
    workflow = await pilot_repo.create_workflow(db, workflow_data)
    await db.flush()

    # 构建响应（不含步骤）
    response_data = PilotWorkflowResponse.model_validate(workflow)
    response_data.steps = []
    return success_response(data=response_data)


@router.get("/pilot/workflow", summary="获取中试研究列表")
async def get_pilot_workflows(
    status: str | None = Query(None, description="状态筛选"),
    keyword: str | None = Query(None, description="搜索产品名称"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    workflows, total = await pilot_repo.get_workflows(
        db, status=status, keyword=keyword, page=page, page_size=page_size
    )

    # 获取每个工作流的步骤数
    items = []
    for wf in workflows:
        steps = await pilot_repo.get_workflow_steps(db, wf.id)
        completed = sum(1 for s in steps if s.status == "completed")
        item = PilotWorkflowListResponse.model_validate(wf)
        item.step_count = len(steps)
        item.completed_step_count = completed
        items.append(item)

    return paginated_response(
        data=items,
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/pilot/workflow/{workflow_id}", summary="获取工作流详情")
async def get_pilot_workflow_detail(
    workflow_id: uuid_module.UUID,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    workflow = await pilot_repo.get_workflow_by_id(db, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")

    steps = await pilot_repo.get_workflow_steps(db, workflow_id)
    response_data = PilotWorkflowResponse.model_validate(workflow)
    response_data.steps = [
        PilotWorkflowStepResponse.model_validate(s) for s in steps
    ]
    return success_response(data=response_data)


@router.post("/pilot/workflow/{workflow_id}/start", summary="启动工作流执行")
async def start_pilot_workflow(
    workflow_id: uuid_module.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    workflow = await pilot_repo.get_workflow_by_id(db, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")

    if workflow.status != "pending":
        raise HTTPException(status_code=400, detail=f"工作流状态为 {workflow.status}，无法启动")

    # 异步启动工作流
    await start_workflow_engine(workflow_id)

    return success_response(data={"message": "工作流已启动", "workflow_id": str(workflow_id)})




@router.post("/pilot/workflow/{workflow_id}/approve", summary="确认当前步骤并执行下一步")
async def approve_pilot_workflow_step(
    workflow_id: uuid_module.UUID,
    current_user: CurrentUser = None,
) -> JSONResponse:
    result = await approve_step_engine(workflow_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return success_response(data=result)

@router.get("/pilot/workflow/{workflow_id}/steps/{step_id}", summary="获取步骤详情")
async def get_pilot_workflow_step(
    workflow_id: uuid_module.UUID,
    step_id: uuid_module.UUID,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    step = await pilot_repo.get_workflow_step_by_id(db, step_id)
    if not step or step.workflow_id != workflow_id:
        raise HTTPException(status_code=404, detail="步骤不存在")

    return success_response(
        data=PilotWorkflowStepResponse.model_validate(step)
    )


@router.post("/pilot/workflow/{workflow_id}/upload", summary="上传工艺文档")
async def upload_pilot_document(
    workflow_id: uuid_module.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    workflow = await pilot_repo.get_workflow_by_id(db, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")

    if workflow.status != "pending":
        raise HTTPException(status_code=400, detail="只有 pending 状态的工作流可以上传文档")

    # 保存文件
    upload_dir = "storage/pilot_workflow"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(
        upload_dir, f"{workflow_id}_{file.filename}"
    )
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # 更新工作流
    workflow.input_document_path = file_path
    await db.flush()

    return success_response(
        data={
            "file_path": file_path,
            "filename": file.filename,
            "file_size": len(content),
        }
    )


@router.delete("/pilot/workflow/{workflow_id}", summary="删除工作流")
async def delete_pilot_workflow(
    workflow_id: uuid_module.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
) -> JSONResponse:
    workflow = await pilot_repo.get_workflow_by_id(db, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")

    # Soft delete
    workflow.is_deleted = True
    workflow.updated_by = current_user.id if current_user else None
    await db.flush()

    return success_response(data={"id": str(workflow_id)})
