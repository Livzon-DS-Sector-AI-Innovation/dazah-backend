"""HR business request and response schemas live here."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# ─── Department Schemas ───

class DepartmentBase(BaseModel):
    name: str = Field(..., max_length=64, description="部门名称")
    code: str = Field(..., max_length=32, description="部门编码")
    description: str | None = Field(None, max_length=256, description="部门描述")


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: str | None = Field(None, max_length=64)
    code: str | None = Field(None, max_length=32)
    description: str | None = Field(None, max_length=256)


class DepartmentResponse(DepartmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None


# ─── Team Schemas ───

class TeamBase(BaseModel):
    name: str = Field(..., max_length=64, description="班组名称")
    code: str | None = Field(None, max_length=32, description="班组编码")
    description: str | None = Field(None, max_length=256, description="班组描述")
    department_id: UUID = Field(..., description="所属部门ID")


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    name: str | None = Field(None, max_length=64)
    code: str | None = Field(None, max_length=32)
    description: str | None = Field(None, max_length=256)
    department_id: UUID | None = Field(None)


class TeamResponse(TeamBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    department: DepartmentResponse | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


# ─── Employee Schemas ───

class EmployeeBase(BaseModel):
    # Core
    employee_number: str = Field(..., max_length=32, description="工号")
    name: str = Field(..., max_length=64, description="姓名")
    domain_account: str | None = Field(None, max_length=64, description="域账号")

    # Department & job
    department: str = Field(..., max_length=64, description="部门")
    team: str | None = Field(None, max_length=64, description="班组")
    position: str = Field(..., max_length=64, description="职位")
    job_category: str | None = Field(None, max_length=32, description="职类")
    level: str | None = Field(None, max_length=32, description="级别")

    # Qualifications
    qualifications: list[str] | None = Field(None, description="职称／职业资格")
    qualification_type: str | None = Field(None, max_length=32, description="职称类型")

    # Personal
    gender: str | None = Field(None, max_length=8, description="性别")
    native_place: str | None = Field(None, max_length=64, description="籍贯")
    political_status: str | None = Field(None, max_length=32, description="政治面貌")
    marital_status: str | None = Field(None, max_length=16, description="婚姻状况")
    household_type: str | None = Field(None, max_length=16, description="户籍类型")
    status_category: str | None = Field(None, max_length=32, description="统计类别")

    # Birth
    birth_year: int | None = Field(None, description="出生年份")
    birth_month: int | None = Field(None, description="出生月份")
    birth_day: int | None = Field(None, description="出生日期")
    age: int | None = Field(None, description="年龄")

    # Dates
    work_start_date: date | None = Field(None, description="参加工作时间")
    factory_entry_date: date | None = Field(None, description="进厂时间")
    livo_entry_date: date | None = Field(None, description="入丽珠时间")
    hire_date: date = Field(..., description="入职日期")
    graduation_date: date | None = Field(None, description="毕业时间")

    # Computed
    work_years: int | None = Field(None, description="工作年限")
    factory_tenure: str | None = Field(None, max_length=32, description="厂龄")
    company_tenure: str | None = Field(None, max_length=32, description="司龄")

    # Education
    education: str | None = Field(None, max_length=16, description="学历")
    classification: str | None = Field(None, max_length=16, description="分类")
    school: str | None = Field(None, max_length=128, description="毕业学校")
    major: str | None = Field(None, max_length=64, description="专业")

    # ID & address
    id_card: str | None = Field(None, max_length=18, description="身份证号")
    id_card_expiry: str | None = Field(None, max_length=32, description="身份证到期日")
    id_card_address: str | None = Field(None, description="身份证地址|家庭地址")
    current_address: str | None = Field(None, description="现住址")

    # Contract
    contract_type: str | None = Field(None, max_length=32, description="合同期限")
    contract_start_date: date | None = Field(None, description="合同开始日期")
    contract_end_date: date | None = Field(None, description="合同结束日期")
    contract_start_2: date | None = Field(None, description="第二次合同起点")
    contract_end_2: date | None = Field(None, description="第二次合同终止")
    contract_start_3: date | None = Field(None, description="第三次合同起点")
    contract_end_3: date | None = Field(None, description="第三次合同终止")
    contract_start_4: date | None = Field(None, description="第四次合同起点")
    contract_end_4: date | None = Field(None, description="第四次合同终止")

    # Contact
    phone: str | None = Field(None, max_length=32, description="手机")
    email: str | None = Field(None, max_length=128, description="邮箱")
    emergency_contact_name: str | None = Field(
        None, max_length=64, description="紧急联系人姓名"
    )
    emergency_contact_phone: str | None = Field(
        None, max_length=32, description="紧急联系人电话"
    )
    emergency_contact_relation: str | None = Field(
        None, max_length=32, description="紧急联系人关系"
    )

    # Banking & training
    bank_account: str | None = Field(None, max_length=32, description="银行卡号")
    training_id: str | None = Field(None, max_length=32, description="培训档案编号")

    # Other
    transfer_history: str | None = Field(None, description="异动记录")
    remarks: list[str] | None = Field(None, description="备注")
    status: str = Field("待审批", max_length=16, description="状态")


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    model_config = ConfigDict(extra="allow")

    employee_number: str | None = Field(None, max_length=32)
    name: str | None = Field(None, max_length=64)
    domain_account: str | None = Field(None, max_length=64)
    department: str | None = Field(None, max_length=64)
    team: str | None = Field(None, max_length=64)
    position: str | None = Field(None, max_length=64)
    job_category: str | None = Field(None, max_length=32)
    level: str | None = Field(None, max_length=32)
    qualifications: list[str] | None = Field(None)
    qualification_type: str | None = Field(None, max_length=32)
    gender: str | None = Field(None, max_length=8)
    native_place: str | None = Field(None, max_length=64)
    political_status: str | None = Field(None, max_length=32)
    marital_status: str | None = Field(None, max_length=16)
    household_type: str | None = Field(None, max_length=16)
    status_category: str | None = Field(None, max_length=32)
    birth_year: int | None = Field(None)
    birth_month: int | None = Field(None)
    birth_day: int | None = Field(None)
    age: int | None = Field(None)
    work_start_date: date | None = Field(None)
    factory_entry_date: date | None = Field(None)
    livo_entry_date: date | None = Field(None)
    hire_date: date | None = Field(None)
    graduation_date: date | None = Field(None)
    work_years: int | None = Field(None)
    factory_tenure: str | None = Field(None, max_length=32)
    company_tenure: str | None = Field(None, max_length=32)
    education: str | None = Field(None, max_length=16)
    classification: str | None = Field(None, max_length=16)
    school: str | None = Field(None, max_length=128)
    major: str | None = Field(None, max_length=64)
    id_card: str | None = Field(None, max_length=18)
    id_card_expiry: str | None = Field(None, max_length=32)
    id_card_address: str | None = Field(None)
    current_address: str | None = Field(None)
    contract_type: str | None = Field(None, max_length=32)
    contract_start_date: date | None = Field(None)
    contract_end_date: date | None = Field(None)
    contract_start_2: date | None = Field(None)
    contract_end_2: date | None = Field(None)
    contract_start_3: date | None = Field(None)
    contract_end_3: date | None = Field(None)
    contract_start_4: date | None = Field(None)
    contract_end_4: date | None = Field(None)
    phone: str | None = Field(None, max_length=32)
    email: str | None = Field(None, max_length=128)
    emergency_contact_name: str | None = Field(None, max_length=64)
    emergency_contact_phone: str | None = Field(None, max_length=32)
    emergency_contact_relation: str | None = Field(None, max_length=32)
    bank_account: str | None = Field(None, max_length=32)
    training_id: str | None = Field(None, max_length=32)
    transfer_history: str | None = Field(None)
    remarks: list[str] | None = Field(None)
    status: str | None = Field(None, max_length=16)


class EmployeeResponse(EmployeeBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    feishu_record_id: str | None = None
    feishu_synced_at: date | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class SyncStatusResponse(BaseModel):
    local_total: int
    feishu_total: int
    synced_count: int
    unsynced_count: int
    conflict_count: int
    last_sync_at: datetime | None = None


# ─── OffboardingRecord Schemas ───

class OffboardingRecordBase(BaseModel):
    employee_id: UUID = Field(..., description="员工ID")
    offboarding_date: date = Field(..., description="离职日期")
    offboarding_type: str = Field("辞职", max_length=16, description="离职类型")
    reason: str | None = Field(None, max_length=512, description="离职原因")
    handover_status: str = Field("待交接", max_length=16, description="交接状态")
    notes: str | None = Field(None, max_length=512, description="备注")


class OffboardingRecordCreate(OffboardingRecordBase):
    pass


class OffboardingRecordUpdate(BaseModel):
    employee_id: UUID | None = Field(None)
    offboarding_date: date | None = Field(None)
    offboarding_type: str | None = Field(None, max_length=16)
    reason: str | None = Field(None, max_length=512)
    handover_status: str | None = Field(None, max_length=16)
    notes: str | None = Field(None, max_length=512)


class OffboardingRecordResponse(OffboardingRecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    employee: EmployeeResponse | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


# ─── DepartureRecord Schemas ───

class DepartureRecordBase(BaseModel):
    # Basic
    name: str = Field(..., max_length=64, description="姓名")
    department: str = Field(..., max_length=64, description="部门")
    team: str | None = Field(None, max_length=64, description="班组")
    position: str = Field(..., max_length=64, description="职位")
    job_category: str | None = Field(None, max_length=64, description="职类")
    gender: str | None = Field(None, max_length=8, description="性别")
    status_category: str | None = Field(None, max_length=64, description="统计类别")

    # Dates
    livo_entry_date: date | None = Field(None, description="入丽珠时间")
    factory_entry_date: date | None = Field(None, description="进厂时间")
    work_start_date: date | None = Field(None, description="参加工作时间")
    offboarding_date: date | None = Field(None, description="离职日期")
    company_tenure_at_leave: str | None = Field(None, max_length=64, description="离职时司龄")

    # Education
    education: str | None = Field(None, max_length=16, description="学历")
    school: str | None = Field(None, max_length=128, description="毕业学校")
    major: str | None = Field(None, max_length=64, description="专业")
    classification: str | None = Field(None, max_length=16, description="分类")

    # Personal
    id_card: str | None = Field(None, max_length=18, description="身份证号")
    native_place: str | None = Field(None, max_length=64, description="籍贯")
    household_type: str | None = Field(None, max_length=128, description="户籍类型")
    marital_status: str | None = Field(None, max_length=32, description="婚姻状况")
    political_status: str | None = Field(None, max_length=64, description="政治面貌")

    # Contact
    phone: str | None = Field(None, max_length=32, description="手机")
    emergency_contact_phone: str | None = Field(None, max_length=32, description="紧急联系人电话")
    emergency_contact_relation: str | None = Field(None, max_length=64, description="紧急联系人|关系")
    bank_account: str | None = Field(None, max_length=128, description="银行卡号")

    # Contract
    contract_type: str | None = Field(None, max_length=64, description="合同期限")

    # Work history
    transfer_history: str | None = Field(None, description="异动记录")

    # Offboarding specific
    offboarding_type: str = Field("辞职", max_length=16, description="离职类型")
    offboarding_reason: list[str] | None = Field(None, description="离职原因")
    offboarding_reason_2: list[str] | None = Field(None, description="离职原因2")
    offboarding_remarks: list[str] | None = Field(None, description="离职备注")

    # Other
    remarks: str | None = Field(None, description="备注")


class DepartureRecordCreate(DepartureRecordBase):
    pass


class DepartureRecordUpdate(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str | None = Field(None, max_length=64)
    department: str | None = Field(None, max_length=64)
    team: str | None = Field(None, max_length=64)
    position: str | None = Field(None, max_length=64)
    job_category: str | None = Field(None, max_length=32)
    gender: str | None = Field(None, max_length=8)
    status_category: str | None = Field(None, max_length=32)
    livo_entry_date: date | None = Field(None)
    factory_entry_date: date | None = Field(None)
    work_start_date: date | None = Field(None)
    offboarding_date: date | None = Field(None)
    company_tenure_at_leave: str | None = Field(None, max_length=32)
    education: str | None = Field(None, max_length=16)
    school: str | None = Field(None, max_length=128)
    major: str | None = Field(None, max_length=64)
    classification: str | None = Field(None, max_length=16)
    id_card: str | None = Field(None, max_length=18)
    native_place: str | None = Field(None, max_length=64)
    household_type: str | None = Field(None, max_length=16)
    marital_status: str | None = Field(None, max_length=16)
    political_status: str | None = Field(None, max_length=32)
    phone: str | None = Field(None, max_length=32)
    emergency_contact_phone: str | None = Field(None, max_length=32)
    emergency_contact_relation: str | None = Field(None, max_length=32)
    bank_account: str | None = Field(None, max_length=32)
    contract_type: str | None = Field(None, max_length=32)
    transfer_history: str | None = Field(None)
    offboarding_type: str | None = Field(None, max_length=16)
    offboarding_reason: list[str] | None = Field(None)
    offboarding_reason_2: list[str] | None = Field(None)
    offboarding_remarks: list[str] | None = Field(None)
    remarks: list[str] | None = Field(None)


class DepartureRecordResponse(DepartureRecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    feishu_record_id: str | None = None
    feishu_synced_at: date | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


# ─── OnboardingRecord Schemas ───

class OnboardingRecordBase(BaseModel):
    # Core
    seq_number: int | None = Field(None, description="编号")
    employee_number: str = Field(..., max_length=32, description="工号")
    name: str = Field(..., max_length=64, description="姓名")
    domain_account: str | None = Field(None, max_length=64, description="域账号")

    # Department & job
    department: str = Field(..., max_length=64, description="部门")
    team: str | None = Field(None, max_length=64, description="班组")
    position: str = Field(..., max_length=64, description="岗位")
    job_category: str | None = Field(None, max_length=32, description="职类")
    status_category: str | None = Field(None, max_length=32, description="统计类别")

    # Employment status
    is_employed: str | None = Field(None, max_length=8, description="是否在职")

    # Dates
    hire_date: date = Field(..., description="入职时间")
    factory_entry_date: date | None = Field(None, description="进厂时间")
    livo_entry_date: date | None = Field(None, description="入丽珠时间")
    work_start_date: date | None = Field(None, description="参加工作时间")
    graduation_date: date | None = Field(None, description="毕业时间")
    birth_month: int | None = Field(None, description="出生月份")
    birth_day: int | None = Field(None, description="出生日期")

    # Contract
    contract_type: str | None = Field(None, max_length=32, description="合同期限")
    contract_start_date: date | None = Field(None, description="第一次合同起点")
    contract_end_date: date | None = Field(None, description="第一次合同终止")
    contract_start_2: date | None = Field(None, description="第二次合同起点")
    contract_end_2: date | None = Field(None, description="第二次合同终止")
    contract_start_3: date | None = Field(None, description="第三次合同起点")
    contract_end_3: date | None = Field(None, description="第三次合同终止")
    contract_start_4: date | None = Field(None, description="第四次合同起点")
    contract_end_4: date | None = Field(None, description="第四次合同终止")

    # Computed
    age: int | None = Field(None, description="年龄")
    work_years: int | None = Field(None, description="工作年限")
    factory_tenure: str | None = Field(None, max_length=32, description="厂龄")
    company_tenure: str | None = Field(None, max_length=32, description="司龄")
    hire_month: str | None = Field(None, max_length=16, description="入职月份")

    # Education
    school: str | None = Field(None, max_length=128, description="毕业学校")
    education: str | None = Field(None, max_length=16, description="学历")
    major: str | None = Field(None, max_length=64, description="专业")
    classification: str | None = Field(None, max_length=16, description="分类")

    # Personal
    id_card: str | None = Field(None, max_length=18, description="身份证号")
    id_card_expiry: str | None = Field(None, max_length=32, description="身份证到期日")
    id_card_address: str | None = Field(None, description="身份证地址|家庭地址")
    current_address: str | None = Field(None, description="现住址")
    marital_status: str | None = Field(None, max_length=16, description="婚姻状况")
    household_type: str | None = Field(None, max_length=16, description="户籍类型")
    political_status: str | None = Field(None, max_length=32, description="政治面貌")

    # Contact
    phone: str | None = Field(None, max_length=32, description="手机")
    email: str | None = Field(None, max_length=128, description="邮箱")
    emergency_contact_phone: str | None = Field(None, max_length=32, description="紧急联系人电话")
    emergency_contact_relation: str | None = Field(None, max_length=32, description="紧急联系人|关系")

    # Banking
    bank_account: str | None = Field(None, max_length=32, description="银行卡号")
    bank_account_location: str | None = Field(None, max_length=32, description="银行卡开户地")

    # Other
    training_id: str | None = Field(None, max_length=32, description="培训档案编号")
    transfer_history: str | None = Field(None, description="异动记录")
    remarks: list[str] | None = Field(None, description="备注")


class OnboardingRecordCreate(OnboardingRecordBase):
    pass


class OnboardingRecordUpdate(BaseModel):
    model_config = ConfigDict(extra="allow")

    seq_number: int | None = Field(None)
    employee_number: str | None = Field(None, max_length=32)
    name: str | None = Field(None, max_length=64)
    domain_account: str | None = Field(None, max_length=64)
    department: str | None = Field(None, max_length=64)
    team: str | None = Field(None, max_length=64)
    position: str | None = Field(None, max_length=64)
    job_category: str | None = Field(None, max_length=32)
    status_category: str | None = Field(None, max_length=32)
    is_employed: str | None = Field(None, max_length=8)
    hire_date: date | None = Field(None)
    factory_entry_date: date | None = Field(None)
    livo_entry_date: date | None = Field(None)
    work_start_date: date | None = Field(None)
    graduation_date: date | None = Field(None)
    birth_month: int | None = Field(None)
    birth_day: int | None = Field(None)
    contract_type: str | None = Field(None, max_length=32)
    contract_start_date: date | None = Field(None)
    contract_end_date: date | None = Field(None)
    contract_start_2: date | None = Field(None)
    contract_end_2: date | None = Field(None)
    contract_start_3: date | None = Field(None)
    contract_end_3: date | None = Field(None)
    contract_start_4: date | None = Field(None)
    contract_end_4: date | None = Field(None)
    age: int | None = Field(None)
    work_years: int | None = Field(None)
    factory_tenure: str | None = Field(None, max_length=32)
    company_tenure: str | None = Field(None, max_length=32)
    hire_month: str | None = Field(None, max_length=16)
    school: str | None = Field(None, max_length=128)
    education: str | None = Field(None, max_length=16)
    major: str | None = Field(None, max_length=64)
    classification: str | None = Field(None, max_length=16)
    id_card: str | None = Field(None, max_length=18)
    id_card_expiry: str | None = Field(None, max_length=32)
    id_card_address: str | None = Field(None)
    current_address: str | None = Field(None)
    marital_status: str | None = Field(None, max_length=16)
    household_type: str | None = Field(None, max_length=16)
    political_status: str | None = Field(None, max_length=32)
    phone: str | None = Field(None, max_length=32)
    email: str | None = Field(None, max_length=128)
    emergency_contact_phone: str | None = Field(None, max_length=32)
    emergency_contact_relation: str | None = Field(None, max_length=32)
    bank_account: str | None = Field(None, max_length=32)
    bank_account_location: str | None = Field(None, max_length=32)
    training_id: str | None = Field(None, max_length=32)
    transfer_history: str | None = Field(None)
    remarks: list[str] | None = Field(None)


class OnboardingRecordResponse(OnboardingRecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    feishu_record_id: str | None = None
    feishu_synced_at: date | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


# ─── TrainingPlan Schemas ───

class TrainingPlanBase(BaseModel):
    plan_name: str = Field(..., max_length=128, description="培训计划名称")
    training_type: str = Field("新入职", max_length=16, description="培训类型")
    target_departments: list[str] | None = Field(None, description="目标部门列表")
    target_positions: list[str] | None = Field(None, description="目标岗位列表")
    planned_start_date: date | None = Field(None, description="计划开始日期")
    planned_end_date: date | None = Field(None, description="计划结束日期")
    status: str = Field("draft", max_length=16, description="状态")
    approver_name: str | None = Field(None, max_length=64, description="审批人姓名")
    approved_at: datetime | None = Field(None, description="审批时间")
    approval_remarks: str | None = Field(None, max_length=512, description="审批备注")


class TrainingPlanCreate(TrainingPlanBase):
    pass


class TrainingPlanUpdate(BaseModel):
    model_config = ConfigDict(extra="allow")

    plan_name: str | None = Field(None, max_length=128)
    training_type: str | None = Field(None, max_length=16)
    target_departments: list[str] | None = Field(None)
    target_positions: list[str] | None = Field(None)
    planned_start_date: date | None = Field(None)
    planned_end_date: date | None = Field(None)
    status: str | None = Field(None, max_length=16)
    approver_name: str | None = Field(None, max_length=64)
    approved_at: datetime | None = Field(None)
    approval_remarks: str | None = Field(None, max_length=512)


class TrainingPlanResponse(TrainingPlanBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None


# ─── TrainingPlanSop Schemas ───

class TrainingPlanSopBase(BaseModel):
    plan_id: UUID = Field(..., description="所属培训计划ID")
    sop_name: str = Field(..., max_length=128, description="SOP名称")
    sop_code: str | None = Field(None, max_length=32, description="SOP编号")
    description: str | None = Field(None, description="SOP描述")
    duration_minutes: int | None = Field(None, description="培训时长(分钟)")
    version: str | None = Field(None, max_length=16, description="版本号")
    file_url: str | None = Field(None, max_length=512, description="文件链接")


class TrainingPlanSopCreate(TrainingPlanSopBase):
    pass


class TrainingPlanSopUpdate(BaseModel):
    model_config = ConfigDict(extra="allow")

    plan_id: UUID | None = Field(None)
    sop_name: str | None = Field(None, max_length=128)
    sop_code: str | None = Field(None, max_length=32)
    description: str | None = Field(None)
    duration_minutes: int | None = Field(None)
    version: str | None = Field(None, max_length=16)
    file_url: str | None = Field(None, max_length=512)


class TrainingPlanSopResponse(TrainingPlanSopBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None


# ─── TrainingRecord Schemas ───

class TrainingRecordBase(BaseModel):
    plan_id: UUID = Field(..., description="培训计划ID")
    sop_id: UUID | None = Field(None, description="SOP ID")
    employee_id: UUID = Field(..., description="员工ID")
    training_date: date | None = Field(None, description="培训日期")
    trainer_name: str | None = Field(None, max_length=64, description="培训师姓名")
    training_location: str | None = Field(None, max_length=128, description="培训地点")
    completion_status: str = Field("未开始", max_length=16, description="完成状态")
    signature_image_url: str | None = Field(None, max_length=512, description="员工签名图片URL")
    remarks: str | None = Field(None, max_length=512, description="备注")


class TrainingRecordCreate(TrainingRecordBase):
    pass


class TrainingRecordUpdate(BaseModel):
    model_config = ConfigDict(extra="allow")

    plan_id: UUID | None = Field(None)
    sop_id: UUID | None = Field(None)
    employee_id: UUID | None = Field(None)
    training_date: date | None = Field(None)
    trainer_name: str | None = Field(None, max_length=64)
    training_location: str | None = Field(None, max_length=128)
    completion_status: str | None = Field(None, max_length=16)
    signature_image_url: str | None = Field(None, max_length=512)
    remarks: str | None = Field(None, max_length=512)


class TrainingRecordResponse(TrainingRecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None


# ─── TrainingAssessment Schemas ───

class TrainingAssessmentBase(BaseModel):
    plan_id: UUID = Field(..., description="培训计划ID")
    employee_id: UUID = Field(..., description="员工ID")
    assessment_date: date | None = Field(None, description="考核日期")
    assessment_type: str = Field("综合", max_length=16, description="考核类型")
    score: int | None = Field(None, description="得分")
    max_score: int | None = Field(None, description="满分")
    result: str = Field("待考核", max_length=8, description="考核结果")
    assessor_name: str | None = Field(None, max_length=64, description="考核人姓名")
    remarks: str | None = Field(None, max_length=512, description="备注")


class TrainingAssessmentCreate(TrainingAssessmentBase):
    pass


class TrainingAssessmentUpdate(BaseModel):
    model_config = ConfigDict(extra="allow")

    plan_id: UUID | None = Field(None)
    employee_id: UUID | None = Field(None)
    assessment_date: date | None = Field(None)
    assessment_type: str | None = Field(None, max_length=16)
    score: int | None = Field(None)
    max_score: int | None = Field(None)
    result: str | None = Field(None, max_length=8)
    assessor_name: str | None = Field(None, max_length=64)
    remarks: str | None = Field(None, max_length=512)


class TrainingAssessmentResponse(TrainingAssessmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None


# ─── TrainingApproval Schemas ───

class TrainingApprovalBase(BaseModel):
    plan_id: UUID = Field(..., description="培训计划ID")
    employee_id: UUID = Field(..., description="员工ID")
    assessment_id: UUID | None = Field(None, description="关联考核ID")
    approval_status: str = Field("pending", max_length=16, description="审批状态")
    approver_name: str | None = Field(None, max_length=64, description="审批人姓名")
    approved_at: datetime | None = Field(None, description="审批时间")
    approval_remarks: str | None = Field(None, max_length=512, description="审批备注")
    is_qualified: bool | None = Field(None, description="是否合格上岗")


class TrainingApprovalCreate(TrainingApprovalBase):
    pass


class TrainingApprovalUpdate(BaseModel):
    model_config = ConfigDict(extra="allow")

    plan_id: UUID | None = Field(None)
    employee_id: UUID | None = Field(None)
    assessment_id: UUID | None = Field(None)
    approval_status: str | None = Field(None, max_length=16)
    approver_name: str | None = Field(None, max_length=64)
    approved_at: datetime | None = Field(None)
    approval_remarks: str | None = Field(None, max_length=512)
    is_qualified: bool | None = Field(None)


class TrainingApprovalResponse(TrainingApprovalBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None
