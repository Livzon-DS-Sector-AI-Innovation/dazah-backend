"""Safety request and response schemas."""

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


# ==================== Enums ====================


class CheckType(str, Enum):
    """检查类型枚举"""

    DAILY = "daily"
    SPECIAL = "special"
    COMPREHENSIVE = "comprehensive"
    HOLIDAY = "holiday"


CHECK_TYPE_OPTIONS = [
    {"value": CheckType.DAILY, "label": "日常检查"},
    {"value": CheckType.SPECIAL, "label": "专项检查"},
    {"value": CheckType.COMPREHENSIVE, "label": "综合检查"},
    {"value": CheckType.HOLIDAY, "label": "节假日检查"},
]


class HazardType(str, Enum):
    """隐患类型枚举"""

    UNSAFE_CONDITION = "unsafe_condition"
    UNSAFE_ACTION = "unsafe_action"
    MANAGEMENT_DEFECT = "management_defect"
    ENVIRONMENTAL = "environmental"


HAZARD_TYPE_OPTIONS = [
    {"value": HazardType.UNSAFE_CONDITION, "label": "物的不安全状态"},
    {"value": HazardType.UNSAFE_ACTION, "label": "人的不安全行为"},
    {"value": HazardType.MANAGEMENT_DEFECT, "label": "管理缺陷"},
    {"value": HazardType.ENVIRONMENTAL, "label": "环境因素"},
]


class HazardLevel(str, Enum):
    """隐患等级枚举"""

    GENERAL = "general"
    MAJOR = "major"


HAZARD_LEVEL_OPTIONS = [
    {"value": HazardLevel.GENERAL, "label": "一般隐患"},
    {"value": HazardLevel.MAJOR, "label": "重大隐患"},
]


class AccidentType(str, Enum):
    """事故类型枚举"""

    INJURY = "injury"
    FIRE = "fire"
    EXPLOSION = "explosion"
    LEAKAGE = "leakage"
    EQUIPMENT = "equipment"
    OTHER = "other"


ACCIDENT_TYPE_OPTIONS = [
    {"value": AccidentType.INJURY, "label": "工伤事故"},
    {"value": AccidentType.FIRE, "label": "火灾"},
    {"value": AccidentType.EXPLOSION, "label": "爆炸"},
    {"value": AccidentType.LEAKAGE, "label": "泄漏"},
    {"value": AccidentType.EQUIPMENT, "label": "设备事故"},
    {"value": AccidentType.OTHER, "label": "其他"},
]


class AccidentLevel(str, Enum):
    """事故等级枚举"""

    GENERAL = "general"
    SERIOUS = "serious"
    MAJOR = "major"
    CATASTROPHIC = "catastrophic"


ACCIDENT_LEVEL_OPTIONS = [
    {"value": AccidentLevel.GENERAL, "label": "一般事故"},
    {"value": AccidentLevel.SERIOUS, "label": "较大事故"},
    {"value": AccidentLevel.MAJOR, "label": "重大事故"},
    {"value": AccidentLevel.CATASTROPHIC, "label": "特别重大事故"},
]


class TrainingType(str, Enum):
    """培训类型枚举"""

    INDUCTION = "induction"
    ANNUAL = "annual"
    SPECIAL = "special"
    EMERGENCY = "emergency"


TRAINING_TYPE_OPTIONS = [
    {"value": TrainingType.INDUCTION, "label": "入职培训"},
    {"value": TrainingType.ANNUAL, "label": "年度培训"},
    {"value": TrainingType.SPECIAL, "label": "专项培训"},
    {"value": TrainingType.EMERGENCY, "label": "应急培训"},
]


class TrainingMode(str, Enum):
    """培训方式枚举"""

    ONLINE = "online"
    OFFLINE = "offline"
    BLENDED = "blended"


TRAINING_MODE_OPTIONS = [
    {"value": TrainingMode.ONLINE, "label": "线上"},
    {"value": TrainingMode.OFFLINE, "label": "线下"},
    {"value": TrainingMode.BLENDED, "label": "混合"},
]


# ==================== 安全检查 Schemas ====================


class SafetyCheckBase(BaseModel):
    """安全检查基础模式"""

    check_no: str = Field(..., max_length=64, description="检查编号")
    check_type: CheckType = Field(CheckType.DAILY, description="检查类型")
    check_date: datetime = Field(..., description="检查日期")
    department: str | None = Field(None, max_length=100, description="检查部门")
    inspector: uuid.UUID | None = Field(None, description="检查人")
    inspector_name: str | None = Field(None, max_length=100, description="检查人姓名")
    location: str | None = Field(None, max_length=255, description="检查地点")
    findings: str | None = Field(None, description="检查发现")
    result: str | None = Field(None, max_length=32, description="检查结果")
    rectification_required: bool = Field(False, description="是否需要整改")
    rectification_deadline: datetime | None = Field(None, description="整改期限")
    notes: str | None = Field(None, description="备注")


class SafetyCheckCreate(SafetyCheckBase):
    """创建安全检查"""

    pass


class SafetyCheckUpdate(BaseModel):
    """更新安全检查"""

    check_no: str | None = Field(None, max_length=64, description="检查编号")
    check_type: CheckType | None = Field(None, description="检查类型")
    check_date: datetime | None = Field(None, description="检查日期")
    department: str | None = Field(None, max_length=100, description="检查部门")
    inspector: uuid.UUID | None = Field(None, description="检查人")
    inspector_name: str | None = Field(None, max_length=100, description="检查人姓名")
    location: str | None = Field(None, max_length=255, description="检查地点")
    findings: str | None = Field(None, description="检查发现")
    result: str | None = Field(None, max_length=32, description="检查结果")
    rectification_required: bool | None = Field(None, description="是否需要整改")
    rectification_deadline: datetime | None = Field(None, description="整改期限")
    rectification_status: str | None = Field(None, max_length=32, description="整改进度")
    status: str | None = Field(None, max_length=32, description="状态")
    notes: str | None = Field(None, description="备注")


class SafetyCheckResponse(SafetyCheckBase):
    """安全检查响应"""

    id: uuid.UUID
    rectification_status: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 隐患排查 Schemas ====================


class HazardReportBase(BaseModel):
    """隐患报告基础模式"""

    hazard_no: str = Field(..., max_length=64, description="隐患编号")
    hazard_type: HazardType = Field(..., description="隐患类型")
    hazard_level: HazardLevel = Field(HazardLevel.GENERAL, description="隐患等级")
    description: str = Field(..., description="隐患描述")
    location: str | None = Field(None, max_length=255, description="地点/部位")
    discovered_by: uuid.UUID | None = Field(None, description="发现人")
    discovered_by_name: str | None = Field(None, max_length=100, description="发现人姓名")
    discovered_at: datetime = Field(..., description="发现时间")
    department: str | None = Field(None, max_length=100, description="责任部门")
    control_measures: str | None = Field(None, description="管控措施")
    deadline: datetime | None = Field(None, description="整改期限")
    check_id: uuid.UUID | None = Field(None, description="关联检查ID")
    notes: str | None = Field(None, description="备注")


class HazardReportCreate(HazardReportBase):
    """创建隐患报告"""

    pass


class HazardReportUpdate(BaseModel):
    """更新隐患报告"""

    hazard_no: str | None = Field(None, max_length=64, description="隐患编号")
    hazard_type: HazardType | None = Field(None, description="隐患类型")
    hazard_level: HazardLevel | None = Field(None, description="隐患等级")
    description: str | None = Field(None, description="隐患描述")
    location: str | None = Field(None, max_length=255, description="地点/部位")
    department: str | None = Field(None, max_length=100, description="责任部门")
    control_measures: str | None = Field(None, description="管控措施")
    deadline: datetime | None = Field(None, description="整改期限")
    rectification_status: str | None = Field(None, max_length=32, description="整改进度")
    verified_by: uuid.UUID | None = Field(None, description="验证人")
    verified_by_name: str | None = Field(None, max_length=100, description="验证人姓名")
    verified_at: datetime | None = Field(None, description="验证时间")
    status: str | None = Field(None, max_length=32, description="状态")
    notes: str | None = Field(None, description="备注")


class HazardReportResponse(HazardReportBase):
    """隐患报告响应"""

    id: uuid.UUID
    rectification_status: str
    status: str
    verified_by: uuid.UUID | None = None
    verified_by_name: str | None = None
    verified_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 事故管理 Schemas ====================


class AccidentBase(BaseModel):
    """事故基础模式"""

    accident_no: str = Field(..., max_length=64, description="事故编号")
    accident_type: AccidentType = Field(..., description="事故类型")
    accident_level: AccidentLevel = Field(AccidentLevel.GENERAL, description="事故等级")
    happened_at: datetime = Field(..., description="发生时间")
    location: str | None = Field(None, max_length=255, description="发生地点")
    description: str = Field(..., description="事故描述")
    casualties: str | None = Field(None, max_length=255, description="伤亡情况")
    property_damage: float | None = Field(None, ge=0, description="财产损失(元)")
    direct_cause: str | None = Field(None, description="直接原因")
    root_cause: str | None = Field(None, description="根本原因")
    handling_measures: str | None = Field(None, description="处理措施")
    corrective_actions: str | None = Field(None, description="纠正预防措施")
    reported_by: uuid.UUID | None = Field(None, description="报告人")
    reported_by_name: str | None = Field(None, max_length=100, description="报告人姓名")
    reported_at: datetime = Field(..., description="报告时间")
    notes: str | None = Field(None, description="备注")


class AccidentCreate(AccidentBase):
    """创建事故"""

    pass


class AccidentUpdate(BaseModel):
    """更新事故"""

    accident_no: str | None = Field(None, max_length=64, description="事故编号")
    accident_type: AccidentType | None = Field(None, description="事故类型")
    accident_level: AccidentLevel | None = Field(None, description="事故等级")
    happened_at: datetime | None = Field(None, description="发生时间")
    location: str | None = Field(None, max_length=255, description="发生地点")
    description: str | None = Field(None, description="事故描述")
    casualties: str | None = Field(None, max_length=255, description="伤亡情况")
    property_damage: float | None = Field(None, ge=0, description="财产损失(元)")
    direct_cause: str | None = Field(None, description="直接原因")
    root_cause: str | None = Field(None, description="根本原因")
    handling_measures: str | None = Field(None, description="处理措施")
    corrective_actions: str | None = Field(None, description="纠正预防措施")
    status: str | None = Field(None, max_length=32, description="状态")
    investigator: uuid.UUID | None = Field(None, description="调查人")
    investigator_name: str | None = Field(None, max_length=100, description="调查人姓名")
    notes: str | None = Field(None, description="备注")


class AccidentResponse(AccidentBase):
    """事故响应"""

    id: uuid.UUID
    status: str
    investigator: uuid.UUID | None = None
    investigator_name: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 安全培训 Schemas ====================


class SafetyTrainingBase(BaseModel):
    """安全培训基础模式"""

    training_no: str = Field(..., max_length=64, description="培训编号")
    training_name: str = Field(..., max_length=255, description="培训名称")
    training_type: TrainingType = Field(TrainingType.ANNUAL, description="培训类型")
    training_mode: TrainingMode = Field(TrainingMode.OFFLINE, description="培训方式")
    trainer: uuid.UUID | None = Field(None, description="培训讲师")
    trainer_name: str | None = Field(None, max_length=100, description="讲师姓名")
    training_date: datetime = Field(..., description="培训日期")
    duration_hours: float | None = Field(None, ge=0, description="培训时长(小时)")
    location: str | None = Field(None, max_length=255, description="培训地点")
    content: str | None = Field(None, description="培训内容")
    department: str | None = Field(None, max_length=100, description="培训部门")
    notes: str | None = Field(None, description="备注")


class SafetyTrainingCreate(SafetyTrainingBase):
    """创建安全培训"""

    pass


class SafetyTrainingUpdate(BaseModel):
    """更新安全培训"""

    training_no: str | None = Field(None, max_length=64, description="培训编号")
    training_name: str | None = Field(None, max_length=255, description="培训名称")
    training_type: TrainingType | None = Field(None, description="培训类型")
    training_mode: TrainingMode | None = Field(None, description="培训方式")
    trainer: uuid.UUID | None = Field(None, description="培训讲师")
    trainer_name: str | None = Field(None, max_length=100, description="讲师姓名")
    training_date: datetime | None = Field(None, description="培训日期")
    duration_hours: float | None = Field(None, ge=0, description="培训时长(小时)")
    location: str | None = Field(None, max_length=255, description="培训地点")
    content: str | None = Field(None, description="培训内容")
    department: str | None = Field(None, max_length=100, description="培训部门")
    status: str | None = Field(None, max_length=32, description="状态")
    notes: str | None = Field(None, description="备注")


class SafetyTrainingResponse(SafetyTrainingBase):
    """安全培训响应"""

    id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 培训记录 Schemas ====================


class TrainingRecordBase(BaseModel):
    """培训记录基础模式"""

    employee_id: uuid.UUID | None = Field(None, description="员工ID")
    employee_name: str | None = Field(None, max_length=100, description="员工姓名")
    department: str | None = Field(None, max_length=100, description="部门")
    attendance: bool = Field(True, description="是否出席")
    score: float | None = Field(None, ge=0, le=100, description="考核成绩")
    passed: bool | None = Field(None, description="是否合格")
    notes: str | None = Field(None, description="备注")


class TrainingRecordCreate(TrainingRecordBase):
    """创建培训记录"""

    training_id: uuid.UUID


class TrainingRecordUpdate(BaseModel):
    """更新培训记录"""

    employee_id: uuid.UUID | None = Field(None, description="员工ID")
    employee_name: str | None = Field(None, max_length=100, description="员工姓名")
    department: str | None = Field(None, max_length=100, description="部门")
    attendance: bool | None = Field(None, description="是否出席")
    score: float | None = Field(None, ge=0, le=100, description="考核成绩")
    passed: bool | None = Field(None, description="是否合格")
    notes: str | None = Field(None, description="备注")


class TrainingRecordResponse(TrainingRecordBase):
    """培训记录响应"""

    id: uuid.UUID
    training_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
