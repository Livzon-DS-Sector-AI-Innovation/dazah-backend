from uuid import UUID

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import paginated_response, success_response
from app.modules.hr.schemas import (
    DepartureRecordCreate,
    DepartureRecordResponse,
    DepartureRecordUpdate,
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
    EmployeeCreate,
    EmployeeResponse,
    EmployeeUpdate,
    OffboardingRecordCreate,
    OffboardingRecordResponse,
    OffboardingRecordUpdate,
    OnboardingRecordResponse,
    TeamCreate,
    TeamResponse,
    TeamUpdate,
    TrainingApprovalCreate,
    TrainingApprovalResponse,
    TrainingApprovalUpdate,
    TrainingAssessmentCreate,
    TrainingAssessmentResponse,
    TrainingAssessmentUpdate,
    TrainingPlanCreate,
    TrainingPlanResponse,
    TrainingPlanSopCreate,
    TrainingPlanSopResponse,
    TrainingPlanSopUpdate,
    TrainingPlanUpdate,
    TrainingRecordCreate,
    TrainingRecordResponse,
    TrainingRecordUpdate,
)
from app.modules.hr.analysis_api import router as analysis_router
from app.modules.hr.service import (
    DepartureRecordService,
    DepartmentService,
    EmployeeService,
    OffboardingRecordService,
    OnboardingRecordService,
    TeamService,
    TrainingApprovalService,
    TrainingAssessmentService,
    TrainingPlanService,
    TrainingPlanSopService,
    TrainingRecordService,
)
from app.shared.module_api import create_module_router
from app.shared.module_registry import MODULES_BY_CODE
from app.shared.schemas import PageParams

router = create_module_router(MODULES_BY_CODE["hr"])


def get_employee_service(session: AsyncSession = Depends(get_db)) -> EmployeeService:
    return EmployeeService(session)


def get_department_service(
    session: AsyncSession = Depends(get_db),
) -> DepartmentService:
    return DepartmentService(session)


def get_offboarding_service(
    session: AsyncSession = Depends(get_db),
) -> OffboardingRecordService:
    return OffboardingRecordService(session)


def get_team_service(
    session: AsyncSession = Depends(get_db),
) -> TeamService:
    return TeamService(session)


def get_onboarding_service(
    session: AsyncSession = Depends(get_db),
) -> OnboardingRecordService:
    return OnboardingRecordService(session)


def get_departure_service(
    session: AsyncSession = Depends(get_db),
) -> DepartureRecordService:
    return DepartureRecordService(session)


def get_training_plan_service(
    session: AsyncSession = Depends(get_db),
) -> TrainingPlanService:
    return TrainingPlanService(session)


def get_training_plan_sop_service(
    session: AsyncSession = Depends(get_db),
) -> TrainingPlanSopService:
    return TrainingPlanSopService(session)


def get_training_record_service(
    session: AsyncSession = Depends(get_db),
) -> TrainingRecordService:
    return TrainingRecordService(session)


def get_training_assessment_service(
    session: AsyncSession = Depends(get_db),
) -> TrainingAssessmentService:
    return TrainingAssessmentService(session)


def get_training_approval_service(
    session: AsyncSession = Depends(get_db),
) -> TrainingApprovalService:
    return TrainingApprovalService(session)


# ─── Employee Routes ───

@router.get("/employees", summary="员工列表")
async def list_employees(
    department: str | None = Query(None, description="部门筛选"),
    status: str | None = Query(None, description="状态筛选"),
    keyword: str | None = Query(None, description="姓名或工号关键词"),
    page_params: PageParams = Depends(),
    service: EmployeeService = Depends(get_employee_service),
):
    employees, total = await service.list_employees(
        department=department,
        status=status,
        keyword=keyword,
        page=page_params.page,
        page_size=page_params.page_size,
    )
    data = [
        EmployeeResponse.model_validate(e).model_dump(mode="json")
        for e in employees
    ]
    return paginated_response(
        data=data,
        page=page_params.page,
        page_size=page_params.page_size,
        total=total,
    )


@router.post("/employees", summary="创建员工")
async def create_employee(
    payload: EmployeeCreate,
    service: EmployeeService = Depends(get_employee_service),
):
    employee = await service.create_employee(payload)
    return success_response(
        data=EmployeeResponse.model_validate(employee).model_dump(mode="json"),
        message="员工创建成功",
        status_code=201,
    )


@router.post("/employees/sync-from-feishu", summary="从飞书多维表格同步员工数据")
async def sync_employees_from_feishu(
    service: EmployeeService = Depends(get_employee_service),
):
    """手动触发：从飞书多维表格拉取全部员工数据并 upsert 到本地 PG。"""
    stats = await service.sync_from_feishu()
    msg = (
        f"同步完成：新增 {stats['created']} 条，"
        f"更新 {stats['updated']} 条，失败 {stats['failed']} 条"
    )
    return success_response(
        data=stats,
        message=msg,
    )


@router.get("/employees/sync-status", summary="飞书同步状态")
async def get_employee_sync_status(
    service: EmployeeService = Depends(get_employee_service),
):
    """查看本地与飞书的数据同步统计。"""
    status = await service.get_sync_status()
    return success_response(
        data=status.model_dump(mode="json"),
    )


@router.get("/employees/{employee_id}", summary="员工详情")
async def get_employee(
    employee_id: UUID,
    service: EmployeeService = Depends(get_employee_service),
):
    employee = await service.get_employee(employee_id)
    return success_response(
        data=EmployeeResponse.model_validate(employee).model_dump(mode="json"),
    )


@router.put("/employees/{employee_id}", summary="更新员工")
async def update_employee(
    employee_id: UUID,
    payload: EmployeeUpdate,
    service: EmployeeService = Depends(get_employee_service),
):
    employee = await service.update_employee(employee_id, payload)
    return success_response(
        data=EmployeeResponse.model_validate(employee).model_dump(mode="json"),
        message="员工更新成功",
    )


@router.delete("/employees/{employee_id}", summary="删除员工")
async def delete_employee(
    employee_id: UUID,
    service: EmployeeService = Depends(get_employee_service),
):
    await service.delete_employee(employee_id)
    return success_response(message="员工删除成功")


@router.post("/employees/{employee_id}/sync-to-feishu", summary="同步单个员工到飞书")
async def sync_employee_to_feishu(
    employee_id: UUID,
    service: EmployeeService = Depends(get_employee_service),
):
    """将本地单个员工强制同步到飞书多维表格。"""
    record_id = await service.sync_to_feishu(employee_id)
    return success_response(
        data={"feishu_record_id": record_id},
        message="员工已同步到飞书",
    )


@router.post("/webhook/feishu-approval", summary="飞书审批完成回调")
async def feishu_approval_webhook(
    payload: dict,
    service: EmployeeService = Depends(get_employee_service),
):
    """接收飞书审批完成通知，更新员工状态为在职。"""
    employee_number = payload.get("employee_number")
    if not employee_number:
        return success_response(message="缺少工号")

    try:
        employee = await service.approve_employee(employee_number)
        return success_response(
            data=EmployeeResponse.model_validate(employee).model_dump(mode="json"),
            message="员工审批通过，状态已更新为在职",
        )
    except Exception as e:
        return success_response(message=f"审批处理失败: {str(e)}")


# ─── Department Routes ───

@router.get("/departments", summary="部门列表")
async def list_departments(
    keyword: str | None = Query(None, description="部门名称或编码关键词"),
    page_params: PageParams = Depends(),
    service: DepartmentService = Depends(get_department_service),
):
    departments, total = await service.list_departments(
        keyword=keyword,
        page=page_params.page,
        page_size=page_params.page_size,
    )
    data = [
        DepartmentResponse.model_validate(d).model_dump(mode="json")
        for d in departments
    ]
    return paginated_response(
        data=data,
        page=page_params.page,
        page_size=page_params.page_size,
        total=total,
    )


@router.post("/departments", summary="创建部门")
async def create_department(
    payload: DepartmentCreate,
    service: DepartmentService = Depends(get_department_service),
):
    department = await service.create_department(payload)
    return success_response(
        data=DepartmentResponse.model_validate(department).model_dump(mode="json"),
        message="部门创建成功",
        status_code=201,
    )


@router.get("/departments/{department_id}", summary="部门详情")
async def get_department(
    department_id: UUID,
    service: DepartmentService = Depends(get_department_service),
):
    department = await service.get_department(department_id)
    return success_response(
        data=DepartmentResponse.model_validate(department).model_dump(mode="json"),
    )


@router.put("/departments/{department_id}", summary="更新部门")
async def update_department(
    department_id: UUID,
    payload: DepartmentUpdate,
    service: DepartmentService = Depends(get_department_service),
):
    department = await service.update_department(department_id, payload)
    return success_response(
        data=DepartmentResponse.model_validate(department).model_dump(mode="json"),
        message="部门更新成功",
    )


@router.delete("/departments/{department_id}", summary="删除部门")
async def delete_department(
    department_id: UUID,
    service: DepartmentService = Depends(get_department_service),
):
    await service.delete_department(department_id)
    return success_response(message="部门删除成功")


# ─── Team Routes ───

@router.get("/teams", summary="班组列表")
async def list_teams(
    department_id: UUID | None = Query(None, description="部门筛选"),
    keyword: str | None = Query(None, description="班组名称或编码关键词"),
    page_params: PageParams = Depends(),
    service: TeamService = Depends(get_team_service),
):
    teams, total = await service.list_teams(
        department_id=department_id,
        keyword=keyword,
        page=page_params.page,
        page_size=page_params.page_size,
    )
    data = [
        TeamResponse.model_validate(t).model_dump(mode="json")
        for t in teams
    ]
    return paginated_response(
        data=data,
        page=page_params.page,
        page_size=page_params.page_size,
        total=total,
    )


@router.post("/teams", summary="创建班组")
async def create_team(
    payload: TeamCreate,
    service: TeamService = Depends(get_team_service),
):
    team = await service.create_team(payload)
    return success_response(
        data=TeamResponse.model_validate(team).model_dump(mode="json"),
        message="班组创建成功",
        status_code=201,
    )


@router.get("/teams/{team_id}", summary="班组详情")
async def get_team(
    team_id: UUID,
    service: TeamService = Depends(get_team_service),
):
    team = await service.get_team(team_id)
    return success_response(
        data=TeamResponse.model_validate(team).model_dump(mode="json"),
    )


@router.put("/teams/{team_id}", summary="更新班组")
async def update_team(
    team_id: UUID,
    payload: TeamUpdate,
    service: TeamService = Depends(get_team_service),
):
    team = await service.update_team(team_id, payload)
    return success_response(
        data=TeamResponse.model_validate(team).model_dump(mode="json"),
        message="班组更新成功",
    )


@router.delete("/teams/{team_id}", summary="删除班组")
async def delete_team(
    team_id: UUID,
    service: TeamService = Depends(get_team_service),
):
    await service.delete_team(team_id)
    return success_response(message="班组删除成功")


# ─── OffboardingRecord Routes ───

@router.get("/offboarding-records", summary="离职记录列表")
async def list_offboarding_records(
    employee_id: UUID | None = Query(None, description="员工ID筛选"),
    keyword: str | None = Query(None, description="姓名或工号关键词"),
    page_params: PageParams = Depends(),
    service: OffboardingRecordService = Depends(get_offboarding_service),
):
    records, total = await service.list_records(
        employee_id=employee_id,
        keyword=keyword,
        page=page_params.page,
        page_size=page_params.page_size,
    )
    data = [
        OffboardingRecordResponse.model_validate(r).model_dump(mode="json")
        for r in records
    ]
    return paginated_response(
        data=data,
        page=page_params.page,
        page_size=page_params.page_size,
        total=total,
    )


@router.post("/offboarding-records", summary="创建离职记录")
async def create_offboarding_record(
    payload: OffboardingRecordCreate,
    service: OffboardingRecordService = Depends(get_offboarding_service),
):
    record = await service.create_record(payload)
    # 手动构建响应，避免触发未加载的 relationship
    data = {
        "id": str(record.id),
        "employee_id": str(record.employee_id),
        "offboarding_date": (
            record.offboarding_date.isoformat()
            if record.offboarding_date else None
        ),
        "offboarding_type": record.offboarding_type,
        "reason": record.reason,
        "handover_status": record.handover_status,
        "notes": record.notes,
        "created_at": record.created_at.isoformat() if record.created_at else None,
        "updated_at": record.updated_at.isoformat() if record.updated_at else None,
    }
    return success_response(
        data=data,
        message="离职记录创建成功，员工状态已更新为离职",
        status_code=201,
    )


@router.get("/offboarding-records/{record_id}", summary="离职记录详情")
async def get_offboarding_record(
    record_id: UUID,
    service: OffboardingRecordService = Depends(get_offboarding_service),
):
    record = await service.get_record(record_id)
    return success_response(
        data=OffboardingRecordResponse.model_validate(record).model_dump(mode="json"),
    )


@router.put("/offboarding-records/{record_id}", summary="更新离职记录")
async def update_offboarding_record(
    record_id: UUID,
    payload: OffboardingRecordUpdate,
    service: OffboardingRecordService = Depends(get_offboarding_service),
):
    record = await service.update_record(record_id, payload)
    return success_response(
        data=OffboardingRecordResponse.model_validate(record).model_dump(mode="json"),
        message="离职记录更新成功",
    )


@router.delete("/offboarding-records/{record_id}", summary="删除离职记录")
async def delete_offboarding_record(
    record_id: UUID,
    service: OffboardingRecordService = Depends(get_offboarding_service),
):
    await service.delete_record(record_id)
    return success_response(message="离职记录删除成功")


# ─── OnboardingRecord Routes ───

@router.get("/onboarding-records", summary="老厂入职台账列表")
async def list_onboarding_records(
    department: str | None = Query(None, description="部门筛选"),
    position: str | None = Query(None, description="岗位筛选"),
    is_employed: str | None = Query(None, description="是否在职筛选"),
    keyword: str | None = Query(None, description="姓名或工号关键词"),
    sort_by: str = Query("hire_date", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向"),
    page_params: PageParams = Depends(),
    service: OnboardingRecordService = Depends(get_onboarding_service),
):
    records, total = await service.list_records(
        department=department,
        position=position,
        is_employed=is_employed,
        keyword=keyword,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page_params.page,
        page_size=page_params.page_size,
    )
    data = [
        OnboardingRecordResponse.model_validate(r).model_dump(mode="json")
        for r in records
    ]
    return paginated_response(
        data=data,
        page=page_params.page,
        page_size=page_params.page_size,
        total=total,
    )


@router.post("/onboarding-records/sync-from-feishu", summary="从飞书同步老厂入职台账")
async def sync_onboarding_from_feishu(
    service: OnboardingRecordService = Depends(get_onboarding_service),
):
    """手动触发：从飞书多维表格拉取全部老厂入职数据并 upsert 到本地 PG。"""
    stats = await service.sync_from_feishu()
    msg = (
        f"同步完成：新增 {stats['created']} 条，"
        f"更新 {stats['updated']} 条，失败 {stats['failed']} 条"
    )
    return success_response(
        data=stats,
        message=msg,
    )


@router.get("/onboarding-records/sync-status", summary="老厂入职台账同步状态")
async def get_onboarding_sync_status(
    service: OnboardingRecordService = Depends(get_onboarding_service),
):
    """查看本地与飞书的数据同步统计。"""
    status = await service.get_sync_status()
    return success_response(
        data=status.model_dump(mode="json"),
    )


@router.get("/onboarding-records/{record_id}", summary="入职记录详情")
async def get_onboarding_record(
    record_id: UUID,
    service: OnboardingRecordService = Depends(get_onboarding_service),
):
    record = await service.get_record(record_id)
    return success_response(
        data=OnboardingRecordResponse.model_validate(record).model_dump(mode="json"),
    )


# ─── DepartureRecord Routes ───

@router.get("/departure-records", summary="老厂离职台账列表")
async def list_departure_records(
    department: str | None = Query(None, description="部门筛选"),
    offboarding_type: str | None = Query(None, description="离职类型筛选"),
    keyword: str | None = Query(None, description="姓名/部门/职位关键词"),
    sort_by: str = Query("offboarding_date", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向"),
    page_params: PageParams = Depends(),
    service: DepartureRecordService = Depends(get_departure_service),
):
    records, total = await service.list_records(
        department=department,
        offboarding_type=offboarding_type,
        keyword=keyword,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page_params.page,
        page_size=page_params.page_size,
    )
    data = [
        DepartureRecordResponse.model_validate(r).model_dump(mode="json")
        for r in records
    ]
    return paginated_response(
        data=data,
        page=page_params.page,
        page_size=page_params.page_size,
        total=total,
    )


@router.post("/departure-records", summary="创建离职台账记录")
async def create_departure_record(
    payload: DepartureRecordCreate,
    service: DepartureRecordService = Depends(get_departure_service),
):
    record = await service.create_record(payload)
    return success_response(
        data=DepartureRecordResponse.model_validate(record).model_dump(mode="json"),
        message="离职台账记录创建成功",
        status_code=201,
    )


@router.get("/departure-records/{record_id}", summary="离职台账记录详情")
async def get_departure_record(
    record_id: UUID,
    service: DepartureRecordService = Depends(get_departure_service),
):
    record = await service.get_record(record_id)
    return success_response(
        data=DepartureRecordResponse.model_validate(record).model_dump(mode="json"),
    )


@router.put("/departure-records/{record_id}", summary="更新离职台账记录")
async def update_departure_record(
    record_id: UUID,
    payload: DepartureRecordUpdate,
    service: DepartureRecordService = Depends(get_departure_service),
):
    record = await service.update_record(record_id, payload)
    return success_response(
        data=DepartureRecordResponse.model_validate(record).model_dump(mode="json"),
        message="离职台账记录更新成功",
    )


@router.delete("/departure-records/{record_id}", summary="删除离职台账记录")
async def delete_departure_record(
    record_id: UUID,
    service: DepartureRecordService = Depends(get_departure_service),
):
    await service.delete_record(record_id)
    return success_response(message="离职台账记录删除成功")


@router.post("/departure-records/sync-from-feishu", summary="从飞书同步老厂离职台账")
async def sync_departure_from_feishu(
    service: DepartureRecordService = Depends(get_departure_service),
):
    """手动触发：从飞书多维表格拉取全部老厂离职数据并 upsert 到本地 PG。"""
    stats = await service.sync_from_feishu()
    msg = (
        f"同步完成：新增 {stats['created']} 条，"
        f"更新 {stats['updated']} 条，失败 {stats['failed']} 条"
    )
    return success_response(
        data=stats,
        message=msg,
    )


@router.get("/departure-records/sync-status", summary="老厂离职台账同步状态")
async def get_departure_sync_status(
    service: DepartureRecordService = Depends(get_departure_service),
):
    """查看本地与飞书的数据同步统计。"""
    status = await service.get_sync_status()
    return success_response(
        data=status.model_dump(mode="json"),
    )


# ─── TrainingPlan Routes ───

@router.get("/training-plans", summary="培训计划列表")
async def list_training_plans(
    training_type: str | None = Query(None, description="培训类型筛选"),
    status: str | None = Query(None, description="状态筛选"),
    keyword: str | None = Query(None, description="计划名称关键词"),
    page_params: PageParams = Depends(),
    service: TrainingPlanService = Depends(get_training_plan_service),
):
    plans, total = await service.list_plans(
        training_type=training_type,
        status=status,
        keyword=keyword,
        page=page_params.page,
        page_size=page_params.page_size,
    )
    data = [
        TrainingPlanResponse.model_validate(p).model_dump(mode="json")
        for p in plans
    ]
    return paginated_response(
        data=data,
        page=page_params.page,
        page_size=page_params.page_size,
        total=total,
    )


@router.post("/training-plans", summary="创建培训计划")
async def create_training_plan(
    payload: TrainingPlanCreate,
    service: TrainingPlanService = Depends(get_training_plan_service),
):
    plan = await service.create_plan(payload)
    return success_response(
        data=TrainingPlanResponse.model_validate(plan).model_dump(mode="json"),
        message="培训计划创建成功",
        status_code=201,
    )


@router.get("/training-plans/{plan_id}", summary="培训计划详情")
async def get_training_plan(
    plan_id: UUID,
    service: TrainingPlanService = Depends(get_training_plan_service),
):
    plan = await service.get_plan(plan_id)
    return success_response(
        data=TrainingPlanResponse.model_validate(plan).model_dump(mode="json"),
    )


@router.put("/training-plans/{plan_id}", summary="更新培训计划")
async def update_training_plan(
    plan_id: UUID,
    payload: TrainingPlanUpdate,
    service: TrainingPlanService = Depends(get_training_plan_service),
):
    plan = await service.update_plan(plan_id, payload)
    return success_response(
        data=TrainingPlanResponse.model_validate(plan).model_dump(mode="json"),
        message="培训计划更新成功",
    )


@router.delete("/training-plans/{plan_id}", summary="删除培训计划")
async def delete_training_plan(
    plan_id: UUID,
    service: TrainingPlanService = Depends(get_training_plan_service),
):
    await service.delete_plan(plan_id)
    return success_response(message="培训计划删除成功")


# ─── TrainingPlanSop Routes ───

@router.get("/training-plan-sops", summary="培训计划SOP列表")
async def list_training_plan_sops(
    plan_id: UUID | None = Query(None, description="培训计划ID筛选"),
    keyword: str | None = Query(None, description="SOP名称关键词"),
    page_params: PageParams = Depends(),
    service: TrainingPlanSopService = Depends(get_training_plan_sop_service),
):
    sops, total = await service.list_sops(
        plan_id=plan_id,
        keyword=keyword,
        page=page_params.page,
        page_size=page_params.page_size,
    )
    data = [
        TrainingPlanSopResponse.model_validate(s).model_dump(mode="json")
        for s in sops
    ]
    return paginated_response(
        data=data,
        page=page_params.page,
        page_size=page_params.page_size,
        total=total,
    )


@router.post("/training-plan-sops", summary="创建培训计划SOP")
async def create_training_plan_sop(
    payload: TrainingPlanSopCreate,
    service: TrainingPlanSopService = Depends(get_training_plan_sop_service),
):
    sop = await service.create_sop(payload)
    return success_response(
        data=TrainingPlanSopResponse.model_validate(sop).model_dump(mode="json"),
        message="培训计划SOP创建成功",
        status_code=201,
    )


@router.get("/training-plan-sops/{sop_id}", summary="培训计划SOP详情")
async def get_training_plan_sop(
    sop_id: UUID,
    service: TrainingPlanSopService = Depends(get_training_plan_sop_service),
):
    sop = await service.get_sop(sop_id)
    return success_response(
        data=TrainingPlanSopResponse.model_validate(sop).model_dump(mode="json"),
    )


@router.put("/training-plan-sops/{sop_id}", summary="更新培训计划SOP")
async def update_training_plan_sop(
    sop_id: UUID,
    payload: TrainingPlanSopUpdate,
    service: TrainingPlanSopService = Depends(get_training_plan_sop_service),
):
    sop = await service.update_sop(sop_id, payload)
    return success_response(
        data=TrainingPlanSopResponse.model_validate(sop).model_dump(mode="json"),
        message="培训计划SOP更新成功",
    )


@router.delete("/training-plan-sops/{sop_id}", summary="删除培训计划SOP")
async def delete_training_plan_sop(
    sop_id: UUID,
    service: TrainingPlanSopService = Depends(get_training_plan_sop_service),
):
    await service.delete_sop(sop_id)
    return success_response(message="培训计划SOP删除成功")


# ─── TrainingRecord Routes ───

@router.get("/training-records", summary="培训记录列表")
async def list_training_records(
    plan_id: UUID | None = Query(None, description="培训计划ID筛选"),
    employee_id: UUID | None = Query(None, description="员工ID筛选"),
    completion_status: str | None = Query(None, description="完成状态筛选"),
    keyword: str | None = Query(None, description="备注关键词"),
    page_params: PageParams = Depends(),
    service: TrainingRecordService = Depends(get_training_record_service),
):
    records, total = await service.list_records(
        plan_id=plan_id,
        employee_id=employee_id,
        completion_status=completion_status,
        keyword=keyword,
        page=page_params.page,
        page_size=page_params.page_size,
    )
    data = [
        TrainingRecordResponse.model_validate(r).model_dump(mode="json")
        for r in records
    ]
    return paginated_response(
        data=data,
        page=page_params.page,
        page_size=page_params.page_size,
        total=total,
    )


@router.post("/training-records", summary="创建培训记录")
async def create_training_record(
    payload: TrainingRecordCreate,
    service: TrainingRecordService = Depends(get_training_record_service),
):
    record = await service.create_record(payload)
    return success_response(
        data=TrainingRecordResponse.model_validate(record).model_dump(mode="json"),
        message="培训记录创建成功",
        status_code=201,
    )


@router.get("/training-records/{record_id}", summary="培训记录详情")
async def get_training_record(
    record_id: UUID,
    service: TrainingRecordService = Depends(get_training_record_service),
):
    record = await service.get_record(record_id)
    return success_response(
        data=TrainingRecordResponse.model_validate(record).model_dump(mode="json"),
    )


@router.put("/training-records/{record_id}", summary="更新培训记录")
async def update_training_record(
    record_id: UUID,
    payload: TrainingRecordUpdate,
    service: TrainingRecordService = Depends(get_training_record_service),
):
    record = await service.update_record(record_id, payload)
    return success_response(
        data=TrainingRecordResponse.model_validate(record).model_dump(mode="json"),
        message="培训记录更新成功",
    )


@router.delete("/training-records/{record_id}", summary="删除培训记录")
async def delete_training_record(
    record_id: UUID,
    service: TrainingRecordService = Depends(get_training_record_service),
):
    await service.delete_record(record_id)
    return success_response(message="培训记录删除成功")


# ─── TrainingAssessment Routes ───

@router.get("/training-assessments", summary="培训考核列表")
async def list_training_assessments(
    plan_id: UUID | None = Query(None, description="培训计划ID筛选"),
    employee_id: UUID | None = Query(None, description="员工ID筛选"),
    result: str | None = Query(None, description="考核结果筛选"),
    keyword: str | None = Query(None, description="备注关键词"),
    page_params: PageParams = Depends(),
    service: TrainingAssessmentService = Depends(get_training_assessment_service),
):
    assessments, total = await service.list_assessments(
        plan_id=plan_id,
        employee_id=employee_id,
        result=result,
        keyword=keyword,
        page=page_params.page,
        page_size=page_params.page_size,
    )
    data = [
        TrainingAssessmentResponse.model_validate(a).model_dump(mode="json")
        for a in assessments
    ]
    return paginated_response(
        data=data,
        page=page_params.page,
        page_size=page_params.page_size,
        total=total,
    )


@router.post("/training-assessments", summary="创建培训考核")
async def create_training_assessment(
    payload: TrainingAssessmentCreate,
    service: TrainingAssessmentService = Depends(get_training_assessment_service),
):
    assessment = await service.create_assessment(payload)
    return success_response(
        data=TrainingAssessmentResponse.model_validate(assessment).model_dump(mode="json"),
        message="培训考核创建成功",
        status_code=201,
    )


@router.get("/training-assessments/{assessment_id}", summary="培训考核详情")
async def get_training_assessment(
    assessment_id: UUID,
    service: TrainingAssessmentService = Depends(get_training_assessment_service),
):
    assessment = await service.get_assessment(assessment_id)
    return success_response(
        data=TrainingAssessmentResponse.model_validate(assessment).model_dump(mode="json"),
    )


@router.put("/training-assessments/{assessment_id}", summary="更新培训考核")
async def update_training_assessment(
    assessment_id: UUID,
    payload: TrainingAssessmentUpdate,
    service: TrainingAssessmentService = Depends(get_training_assessment_service),
):
    assessment = await service.update_assessment(assessment_id, payload)
    return success_response(
        data=TrainingAssessmentResponse.model_validate(assessment).model_dump(mode="json"),
        message="培训考核更新成功",
    )


@router.delete("/training-assessments/{assessment_id}", summary="删除培训考核")
async def delete_training_assessment(
    assessment_id: UUID,
    service: TrainingAssessmentService = Depends(get_training_assessment_service),
):
    await service.delete_assessment(assessment_id)
    return success_response(message="培训考核删除成功")


# ─── TrainingApproval Routes ───

@router.get("/training-approvals", summary="培训审批列表")
async def list_training_approvals(
    plan_id: UUID | None = Query(None, description="培训计划ID筛选"),
    employee_id: UUID | None = Query(None, description="员工ID筛选"),
    approval_status: str | None = Query(None, description="审批状态筛选"),
    keyword: str | None = Query(None, description="审批备注关键词"),
    page_params: PageParams = Depends(),
    service: TrainingApprovalService = Depends(get_training_approval_service),
):
    approvals, total = await service.list_approvals(
        plan_id=plan_id,
        employee_id=employee_id,
        approval_status=approval_status,
        keyword=keyword,
        page=page_params.page,
        page_size=page_params.page_size,
    )
    data = [
        TrainingApprovalResponse.model_validate(a).model_dump(mode="json")
        for a in approvals
    ]
    return paginated_response(
        data=data,
        page=page_params.page,
        page_size=page_params.page_size,
        total=total,
    )


@router.post("/training-approvals", summary="创建培训审批")
async def create_training_approval(
    payload: TrainingApprovalCreate,
    service: TrainingApprovalService = Depends(get_training_approval_service),
):
    approval = await service.create_approval(payload)
    return success_response(
        data=TrainingApprovalResponse.model_validate(approval).model_dump(mode="json"),
        message="培训审批创建成功",
        status_code=201,
    )


@router.get("/training-approvals/{approval_id}", summary="培训审批详情")
async def get_training_approval(
    approval_id: UUID,
    service: TrainingApprovalService = Depends(get_training_approval_service),
):
    approval = await service.get_approval(approval_id)
    return success_response(
        data=TrainingApprovalResponse.model_validate(approval).model_dump(mode="json"),
    )


@router.put("/training-approvals/{approval_id}", summary="更新培训审批")
async def update_training_approval(
    approval_id: UUID,
    payload: TrainingApprovalUpdate,
    service: TrainingApprovalService = Depends(get_training_approval_service),
):
    approval = await service.update_approval(approval_id, payload)
    return success_response(
        data=TrainingApprovalResponse.model_validate(approval).model_dump(mode="json"),
        message="培训审批更新成功",
    )


@router.delete("/training-approvals/{approval_id}", summary="删除培训审批")
async def delete_training_approval(
    approval_id: UUID,
    service: TrainingApprovalService = Depends(get_training_approval_service),
):
    await service.delete_approval(approval_id)
    return success_response(message="培训审批删除成功")


router.include_router(analysis_router)
