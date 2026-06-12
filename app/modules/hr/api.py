import logging
from uuid import UUID

from fastapi import Depends, File, Form, Query, UploadFile

logger = logging.getLogger(__name__)
from fastapi.responses import RedirectResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import paginated_response, success_response
from app.modules.hr.schemas import (
    CandidateListResponse,
    CandidateResponse,
    CandidateUpdate,
    CandidateUpdateRecommendationLevel,
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
)
from app.modules.hr.analysis_api import router as analysis_router
from app.modules.hr.service import (
    CandidateService,
    DepartureRecordService,
    DepartmentService,
    EmployeeService,
    OffboardingRecordService,
    OnboardingRecordService,
    TeamService,
)
from app.platform.integrations.feishu.candidate_datasource import CandidateBitableDataSource
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


def get_candidate_service(
    session: AsyncSession = Depends(get_db),
) -> CandidateService:
    return CandidateService(session)


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


# ─── Candidate Routes ───

@router.get("/candidates", summary="候选人列表")
async def list_candidates(
    position: str | None = Query(None, description="职位筛选"),
    education: str | None = Query(None, description="学历筛选"),
    recommendation_level: str | None = Query(None, description="推荐等级筛选（支持逗号分隔多个值）"),
    sync_status: str | None = Query(None, description="飞书同步状态筛选: synced/failed/unsynced"),
    keyword: str | None = Query(None, description="姓名/职位关键词"),
    page_params: PageParams = Depends(),
    service: CandidateService = Depends(get_candidate_service),
):
    candidates, total = await service.list_candidates(
        position=position,
        education=education,
        recommendation_level=recommendation_level,
        sync_status=sync_status,
        keyword=keyword,
        page=page_params.page,
        page_size=page_params.page_size,
    )
    print("DEBUG API: recommendation_level=" + str(recommendation_level) + ", total=" + str(total), flush=True)
    data = [
        CandidateResponse.model_validate(c).model_dump(mode="json")
        for c in candidates
    ]
    return paginated_response(
        data=data,
        page=page_params.page,
        page_size=page_params.page_size,
        total=total,
    )


@router.post("/candidates/parse-preview", summary="预览简历AI解析结果")
async def preview_resume_parse(
    resume: UploadFile = File(..., description="简历 PDF 附件"),
    position: str = Form(..., max_length=64, description="应聘职位名称"),
    service: CandidateService = Depends(get_candidate_service),
):
    """上传简历 PDF，转为图片后由 AI 视觉识别并返回预览字段（不保存）。"""
    resume_bytes = await resume.read()
    result = await service.parse_resume_preview(resume_bytes, position)
    return success_response(data=result)


@router.post("/candidates", summary="新建候选人")
async def create_candidate(
    name: str = Form(..., max_length=64, description="候选人姓名"),
    position: str = Form(..., max_length=64, description="应聘职位名称"),
    resume: UploadFile = File(..., description="简历 PDF 附件"),
    gender: str | None = Form(None, max_length=8, description="性别"),
    school: str | None = Form(None, max_length=128, description="学校名称"),
    education: str | None = Form(None, max_length=16, description="学历"),
    major: str | None = Form(None, max_length=64, description="专业"),
    match_report: str | None = Form(None, description="AI 匹配度报告"),
    recommendation_level: str | None = Form(
        None, max_length=16, description="推荐等级"
    ),
    service: CandidateService = Depends(get_candidate_service),
):
    """手动新建候选人：上传简历 PDF，创建本地记录并同步到飞书。"""
    resume_bytes = await resume.read()
    candidate = await service.create_candidate_with_resume(
        name=name,
        position=position,
        resume_bytes=resume_bytes,
        filename=resume.filename or f"{name}.pdf",
        gender=gender,
        school=school,
        education=education,
        major=major,
        match_report=match_report,
        recommendation_level=recommendation_level,
    )
    return success_response(
        data=CandidateResponse.model_validate(candidate).model_dump(mode="json"),
        message="候选人创建成功",
    )


@router.post("/candidates/sync-from-feishu", summary="从飞书同步候选人数据")
async def sync_candidates_from_feishu(
    service: CandidateService = Depends(get_candidate_service),
):
    """手动触发：从飞书多维表格拉取全部候选人数据并 upsert 到本地 PG。"""
    stats = await service.sync_from_feishu()
    msg = (
        f"同步完成：新增 {stats['created']} 条，"
        f"更新 {stats['updated']} 条，失败 {stats['failed']} 条"
    )
    return success_response(
        data=stats,
        message=msg,
    )


@router.get("/candidates/sync-status", summary="候选人同步状态")
async def get_candidates_sync_status(
    service: CandidateService = Depends(get_candidate_service),
):
    """查看本地与飞书的候选人数据同步统计。"""
    status = await service.get_sync_status()
    return success_response(
        data=status.model_dump(mode="json"),
    )


@router.post("/candidates/{candidate_id}/sync-to-feishu", summary="同步候选人到飞书")
async def sync_candidate_to_feishu(
    candidate_id: UUID,
    service: CandidateService = Depends(get_candidate_service),
):
    """手动触发：将单个候选人（含简历）同步到飞书多维表格。"""
    candidate = await service.sync_candidate_to_feishu(candidate_id)
    return success_response(
        data=CandidateResponse.model_validate(candidate).model_dump(mode="json"),
        message="候选人与简历已同步到飞书",
    )


@router.get("/candidates/{candidate_id}", summary="候选人详情")
async def get_candidate(
    candidate_id: UUID,
    service: CandidateService = Depends(get_candidate_service),
):
    candidate = await service.get_candidate(candidate_id)
    return success_response(
        data=CandidateResponse.model_validate(candidate).model_dump(mode="json"),
    )


@router.put("/candidates/{candidate_id}", summary="更新候选人信息")
async def update_candidate(
    candidate_id: UUID,
    payload: CandidateUpdate,
    service: CandidateService = Depends(get_candidate_service),
):
    candidate = await service.update_candidate(candidate_id, payload)
    return success_response(
        data=CandidateResponse.model_validate(candidate).model_dump(mode="json"),
        message="候选人信息更新成功",
    )


@router.delete("/candidates/{candidate_id}", summary="删除候选人")
async def delete_candidate(
    candidate_id: UUID,
    service: CandidateService = Depends(get_candidate_service),
):
    await service.delete_candidate(candidate_id)
    return success_response(message="候选人删除成功")


@router.put("/candidates/{candidate_id}/recommendation-level", summary="更新候选人推荐等级")
async def update_candidate_recommendation_level(
    candidate_id: UUID,
    payload: CandidateUpdateRecommendationLevel,
    service: CandidateService = Depends(get_candidate_service),
):
    candidate = await service.update_recommendation_level(
        candidate_id, payload.recommendation_level
    )
    return success_response(
        data=CandidateResponse.model_validate(candidate).model_dump(mode="json"),
        message="推荐等级更新成功",
    )


@router.get("/candidates/{candidate_id}/resume-preview", summary="简历预览")
async def preview_candidate_resume(
    candidate_id: UUID,
    service: CandidateService = Depends(get_candidate_service),
):
    """获取候选人简历 PDF。优先读取本地存储，若不存在则从飞书下载。"""
    import os

    from app.core.exceptions import NotFoundException

    candidate = await service.get_candidate(candidate_id)

    # 优先读取本地文件
    if candidate.resume_storage_path and os.path.exists(candidate.resume_storage_path):
        def iter_file():
            with open(candidate.resume_storage_path, "rb") as f:
                while chunk := f.read(64 * 1024):
                    yield chunk

        return StreamingResponse(
            content=iter_file(),
            media_type="application/pdf",
            headers={"Content-Disposition": f'inline; filename="resume.pdf"'},
        )

    # 回退：从飞书实时下载
    attachments = candidate.resume_attachments or []
    if not attachments:
        raise NotFoundException("简历附件", str(candidate_id))

    file_token = attachments[0].get("file_token")
    if not file_token:
        raise NotFoundException("简历附件", str(candidate_id))

    try:
        tmp_download_url = await service.bitable.get_resume_download_url(file_token)
    except Exception as exc:
        logger.warning("Failed to get feishu download url for candidate %s: %s", candidate_id, exc)
        raise NotFoundException("简历附件", str(candidate_id)) from exc

    import httpx
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(tmp_download_url)
        response.raise_for_status()

    return StreamingResponse(
        content=response.iter_bytes(),
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="resume.pdf"'},
    )


router.include_router(analysis_router)
