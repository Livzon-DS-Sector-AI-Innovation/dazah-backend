from uuid import UUID

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import paginated_response, success_response
from app.modules.hr.schemas import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
    EmployeeCreate,
    EmployeeResponse,
    EmployeeUpdate,
    OffboardingRecordCreate,
    OffboardingRecordResponse,
    OffboardingRecordUpdate,
    TeamCreate,
    TeamResponse,
    TeamUpdate,
)
from app.modules.hr.service import (
    DepartmentService,
    EmployeeService,
    OffboardingRecordService,
    TeamService,
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
