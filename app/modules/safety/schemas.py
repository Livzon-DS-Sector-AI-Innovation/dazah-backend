"""Safety request and response schemas."""

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

# ==================== Enums ====================


class ChangeType(str, Enum):
    """变更类型枚举"""

    PROCESS_TECH = "process_tech"
    EQUIPMENT_FACILITY = "equipment_facility"
    MANAGEMENT = "management"


CHANGE_TYPE_OPTIONS = [
    {"value": ChangeType.PROCESS_TECH, "label": "工艺技术变更"},
    {"value": ChangeType.EQUIPMENT_FACILITY, "label": "设备设施变更"},
    {"value": ChangeType.MANAGEMENT, "label": "管理变更"},
]


class ChangeGrade(str, Enum):
    """变更等级枚举"""

    MAJOR = "major"
    GENERAL = "general"


CHANGE_GRADE_OPTIONS = [
    {"value": ChangeGrade.MAJOR, "label": "重大变更", "color": "red"},
    {"value": ChangeGrade.GENERAL, "label": "一般变更", "color": "blue"},
]


class ChangeDuration(str, Enum):
    """变更期限枚举"""

    PERMANENT = "permanent"
    TEMPORARY = "temporary"
    EMERGENCY = "emergency"


CHANGE_DURATION_OPTIONS = [
    {"value": ChangeDuration.PERMANENT, "label": "永久性"},
    {"value": ChangeDuration.TEMPORARY, "label": "临时性"},
    {"value": ChangeDuration.EMERGENCY, "label": "紧急", "color": "red"},
]


class EhsChangeStatusEnum(str, Enum):
    """EHS变更状态枚举"""

    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMMISSIONED = "commissioned"
    CLOSED = "closed"


EHS_CHANGE_STATUS_OPTIONS = [
    {"value": EhsChangeStatusEnum.DRAFT, "label": "草稿", "color": "default"},
    {"value": EhsChangeStatusEnum.UNDER_REVIEW, "label": "审核中", "color": "processing"},
    {"value": EhsChangeStatusEnum.APPROVED, "label": "已批准", "color": "green"},
    {"value": EhsChangeStatusEnum.REJECTED, "label": "已驳回", "color": "red"},
    {"value": EhsChangeStatusEnum.IN_PROGRESS, "label": "实施中", "color": "orange"},
    {"value": EhsChangeStatusEnum.COMMISSIONED, "label": "已投用", "color": "cyan"},
    {"value": EhsChangeStatusEnum.CLOSED, "label": "已关闭", "color": "default"},
]


class RiskAssessmentMethodEnum(str, Enum):
    """风险评估方法枚举"""

    LEC = "LEC"
    LS = "LS"
    JHA = "JHA"
    HAZOP = "HAZOP"
    FMEA = "FMEA"
    SCL = "SCL"
    PHA = "PHA"
    LOPA = "LOPA"
    OTHER = "other"


RISK_ASSESSMENT_METHOD_OPTIONS = [
    {"value": RiskAssessmentMethodEnum.LEC, "label": "LEC评价法"},
    {"value": RiskAssessmentMethodEnum.LS, "label": "LS风险矩阵"},
    {"value": RiskAssessmentMethodEnum.JHA, "label": "JHA工作危害分析"},
    {"value": RiskAssessmentMethodEnum.HAZOP, "label": "HAZOP分析"},
    {"value": RiskAssessmentMethodEnum.FMEA, "label": "FMEA失效模式分析"},
    {"value": RiskAssessmentMethodEnum.SCL, "label": "SCL安全检查表"},
    {"value": RiskAssessmentMethodEnum.PHA, "label": "PHA预先危险性分析"},
    {"value": RiskAssessmentMethodEnum.LOPA, "label": "LOPA保护层分析"},
    {"value": RiskAssessmentMethodEnum.OTHER, "label": "其他"},
]


class RiskLevelEnum(str, Enum):
    """风险等级枚举"""

    LEVEL_1 = "level_1"
    LEVEL_2 = "level_2"
    LEVEL_3 = "level_3"
    LEVEL_4 = "level_4"


RISK_LEVEL_OPTIONS = [
    {"value": RiskLevelEnum.LEVEL_1, "label": "一级/重大风险", "color": "red"},
    {"value": RiskLevelEnum.LEVEL_2, "label": "二级/较大风险", "color": "orange"},
    {"value": RiskLevelEnum.LEVEL_3, "label": "三级/一般风险", "color": "yellow"},
    {"value": RiskLevelEnum.LEVEL_4, "label": "四级/低风险", "color": "blue"},
]


class ApprovalDecisionEnum(str, Enum):
    """审批决定枚举"""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


APPROVAL_DECISION_OPTIONS = [
    {"value": ApprovalDecisionEnum.PENDING, "label": "待审批", "color": "default"},
    {"value": ApprovalDecisionEnum.APPROVED, "label": "同意", "color": "green"},
    {"value": ApprovalDecisionEnum.REJECTED, "label": "驳回", "color": "red"},
]


class ActionItemStatusEnum(str, Enum):
    """行动项状态枚举"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


ACTION_ITEM_STATUS_OPTIONS = [
    {"value": ActionItemStatusEnum.PENDING, "label": "待完成"},
    {"value": ActionItemStatusEnum.IN_PROGRESS, "label": "进行中"},
    {"value": ActionItemStatusEnum.COMPLETED, "label": "已完成"},
]


class PSSRResultEnum(str, Enum):
    """PSSR检查结果枚举"""

    PASS = "pass"
    FAIL = "fail"
    NA = "na"


PSSR_RESULT_OPTIONS = [
    {"value": PSSRResultEnum.PASS, "label": "通过", "color": "green"},
    {"value": PSSRResultEnum.FAIL, "label": "不通过", "color": "red"},
    {"value": PSSRResultEnum.NA, "label": "不适用", "color": "default"},
]


class CheckType(str, Enum):
    """检查类型枚举（14种）"""

    DAILY = "daily"
    SPECIAL = "special"
    COMPREHENSIVE = "comprehensive"
    HOLIDAY = "holiday"
    MONTHLY = "monthly"
    SEASONAL = "seasonal"
    PRE_HOLIDAY = "pre_holiday"
    LEADERSHIP_DUTY = "leadership_duty"
    DEPT_CROSS = "dept_cross"
    WEEKLY = "weekly"
    RESUMPTION = "resumption"
    CHANGE_ACCEPTANCE = "change_acceptance"
    LIGHTNING = "lightning"
    SAFETY_VALVE = "safety_valve"
    POST_HOLIDAY = "post_holiday"
    HEATSTROKE_PREVENTION = "heatstroke_prevention"


CHECK_TYPE_OPTIONS = [
    {"value": CheckType.DAILY, "label": "日常检查"},
    {"value": CheckType.SPECIAL, "label": "专项检查"},
    {"value": CheckType.COMPREHENSIVE, "label": "综合检查"},
    {"value": CheckType.HOLIDAY, "label": "节假日检查"},
    {"value": CheckType.MONTHLY, "label": "月度安全检查"},
    {"value": CheckType.SEASONAL, "label": "季节性安全检查"},
    {"value": CheckType.PRE_HOLIDAY, "label": "节前安全检查"},
    {"value": CheckType.LEADERSHIP_DUTY, "label": "领导干部值班检查"},
    {"value": CheckType.DEPT_CROSS, "label": "部门互查"},
    {"value": CheckType.WEEKLY, "label": "周检"},
    {"value": CheckType.RESUMPTION, "label": "复工复产安全检查"},
    {"value": CheckType.CHANGE_ACCEPTANCE, "label": "变更验收"},
    {"value": CheckType.LIGHTNING, "label": "防雷检查"},
    {"value": CheckType.SAFETY_VALVE, "label": "安全阀专项检查"},
    {"value": CheckType.POST_HOLIDAY, "label": "节后复工检查"},
    {"value": CheckType.HEATSTROKE_PREVENTION, "label": "防暑降温专项"},
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
    """隐患等级枚举（三级）"""

    GENERAL = "general"    # 一般隐患
    SERIOUS = "serious"    # 较大隐患
    MAJOR = "major"        # 重大隐患


HAZARD_LEVEL_OPTIONS = [
    {"value": HazardLevel.GENERAL, "label": "一般隐患"},
    {"value": HazardLevel.SERIOUS, "label": "较大隐患"},
    {"value": HazardLevel.MAJOR, "label": "重大隐患"},
]


class HazardCategory(str, Enum):
    """隐患类别枚举（13种）"""

    EQUIPMENT = "equipment"
    HAZARDOUS_STORAGE = "hazardous_storage"
    EMERGENCY_MGMT = "emergency_mgmt"
    INSTRUMENT_ELECTRICAL = "instrument_electrical"
    LIGHTNING_ANTISTATIC = "lightning_antistatic"
    OCCUPATIONAL_HEALTH = "occupational_health"
    VIOLATION_OPERATION = "violation_operation"
    SIX_S = "six_s"
    LABEL_SIGNAGE = "label_signage"
    PROCESS_MGMT = "process_mgmt"
    CONTRACTOR_DEFECT = "contractor_defect"
    DOCUMENTATION = "documentation"
    SPECIAL_OPERATION = "special_operation"


HAZARD_CATEGORY_OPTIONS = [
    {"value": HazardCategory.EQUIPMENT, "label": "设备设施"},
    {"value": HazardCategory.HAZARDOUS_STORAGE, "label": "危化储存"},
    {"value": HazardCategory.EMERGENCY_MGMT, "label": "应急管理"},
    {"value": HazardCategory.INSTRUMENT_ELECTRICAL, "label": "仪表+电气"},
    {"value": HazardCategory.LIGHTNING_ANTISTATIC, "label": "防雷防静电"},
    {"value": HazardCategory.OCCUPATIONAL_HEALTH, "label": "职业健康+劳保防护"},
    {"value": HazardCategory.VIOLATION_OPERATION, "label": "三违作业"},
    {"value": HazardCategory.SIX_S, "label": "6S"},
    {"value": HazardCategory.LABEL_SIGNAGE, "label": "标签标识"},
    {"value": HazardCategory.PROCESS_MGMT, "label": "工艺管理"},
    {"value": HazardCategory.CONTRACTOR_DEFECT, "label": "承包商缺陷"},
    {"value": HazardCategory.DOCUMENTATION, "label": "内页资料"},
    {"value": HazardCategory.SPECIAL_OPERATION, "label": "特殊作业"},
]


class AccidentType(str, Enum):
    """事故类型枚举"""

    INJURY = "injury"
    FIRE = "fire"
    EXPLOSION = "explosion"
    LEAKAGE = "leakage"
    EQUIPMENT = "equipment"
    NEAR_MISS = "near_miss"
    ENVIRONMENTAL = "environmental"
    OCCUPATIONAL_DISEASE = "occupational_disease"
    TRAFFIC = "traffic"
    OTHER = "other"


ACCIDENT_TYPE_OPTIONS = [
    {"value": AccidentType.INJURY, "label": "工伤事故"},
    {"value": AccidentType.FIRE, "label": "火灾"},
    {"value": AccidentType.EXPLOSION, "label": "爆炸"},
    {"value": AccidentType.LEAKAGE, "label": "泄漏"},
    {"value": AccidentType.EQUIPMENT, "label": "设备事故"},
    {"value": AccidentType.NEAR_MISS, "label": "未遂事件"},
    {"value": AccidentType.ENVIRONMENTAL, "label": "环境事件"},
    {"value": AccidentType.OCCUPATIONAL_DISEASE, "label": "职业病"},
    {"value": AccidentType.TRAFFIC, "label": "交通事故"},
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


class AccidentStatus(str, Enum):
    """事故处理状态枚举"""

    REPORTED = "reported"
    INVESTIGATING = "investigating"
    INVESTIGATED = "investigated"
    CAPA_IN_PROGRESS = "capa_in_progress"
    CLOSED = "closed"


ACCIDENT_STATUS_OPTIONS = [
    {"value": AccidentStatus.REPORTED, "label": "已报告", "color": "blue"},
    {"value": AccidentStatus.INVESTIGATING, "label": "调查中", "color": "orange"},
    {"value": AccidentStatus.INVESTIGATED, "label": "调查完成", "color": "cyan"},
    {"value": AccidentStatus.CAPA_IN_PROGRESS, "label": "CAPA进行中", "color": "purple"},
    {"value": AccidentStatus.CLOSED, "label": "已关闭", "color": "green"},
]


class InjurySeverity(str, Enum):
    """伤害程度枚举"""

    DEATH = "death"
    SERIOUS_INJURY = "serious_injury"
    MINOR_INJURY = "minor_injury"
    NO_INJURY = "no_injury"


INJURY_SEVERITY_OPTIONS = [
    {"value": InjurySeverity.DEATH, "label": "死亡", "color": "red"},
    {"value": InjurySeverity.SERIOUS_INJURY, "label": "重伤", "color": "orange"},
    {"value": InjurySeverity.MINOR_INJURY, "label": "轻伤", "color": "yellow"},
    {"value": InjurySeverity.NO_INJURY, "label": "无伤害", "color": "green"},
]


class TrainingType(str, Enum):
    """培训类型枚举"""

    INDUCTION = "induction"
    ANNUAL = "annual"
    SPECIAL = "special"
    EMERGENCY = "emergency"
    CONTRACTOR = "contractor"
    REFRESHER = "refresher"


TRAINING_TYPE_OPTIONS = [
    {"value": TrainingType.INDUCTION, "label": "入职培训"},
    {"value": TrainingType.ANNUAL, "label": "年度培训"},
    {"value": TrainingType.SPECIAL, "label": "专项培训"},
    {"value": TrainingType.EMERGENCY, "label": "应急培训"},
    {"value": TrainingType.CONTRACTOR, "label": "承包商培训"},
    {"value": TrainingType.REFRESHER, "label": "复训"},
]


class TrainingMode(str, Enum):
    """培训方式枚举"""

    ONLINE = "online"
    OFFLINE = "offline"
    BLENDED = "blended"


class TrainingLevel(str, Enum):
    """培训级别枚举"""

    COMPANY = "company"
    DEPT = "dept"
    TEAM = "team"


TRAINING_LEVEL_OPTIONS = [
    {"value": TrainingLevel.COMPANY, "label": "公司级"},
    {"value": TrainingLevel.DEPT, "label": "部门级"},
    {"value": TrainingLevel.TEAM, "label": "班组级"},
]


class CertificateStatus(str, Enum):
    """证书状态枚举"""

    VALID = "valid"
    EXPIRING = "expiring"
    EXPIRED = "expired"


CERTIFICATE_STATUS_OPTIONS = [
    {"value": CertificateStatus.VALID, "label": "有效", "color": "green"},
    {"value": CertificateStatus.EXPIRING, "label": "即将到期", "color": "orange"},
    {"value": CertificateStatus.EXPIRED, "label": "已过期", "color": "red"},
]


TRAINING_MODE_OPTIONS = [
    {"value": TrainingMode.ONLINE, "label": "线上"},
    {"value": TrainingMode.OFFLINE, "label": "线下"},
    {"value": TrainingMode.BLENDED, "label": "混合"},
]


class RevisionType(str, Enum):
    """修订类型枚举"""

    MANUAL = "manual"
    AI = "ai"


REVISION_TYPE_OPTIONS = [
    {"value": RevisionType.MANUAL, "label": "人工修订"},
    {"value": RevisionType.AI, "label": "AI修订"},
]


class RevisionScope(str, Enum):
    """修订范围枚举"""

    PROCESS = "process"
    SAFETY_REQUIREMENT = "safety_requirement"


REVISION_SCOPE_OPTIONS = [
    {"value": RevisionScope.PROCESS, "label": "工艺"},
    {"value": RevisionScope.SAFETY_REQUIREMENT, "label": "安全要求"},
]


class ReviewOpinion(str, Enum):
    """审核意见枚举"""

    PENDING = "pending"
    APPROVED = "approved"


REVIEW_OPINION_OPTIONS = [
    {"value": ReviewOpinion.PENDING, "label": "待审核"},
    {"value": ReviewOpinion.APPROVED, "label": "已审核"},
]




class OperationType(str, Enum):
    """特殊作业类型枚举（GB 30871-2022）"""

    HOT_WORK = "hot_work"
    CONFINED_SPACE = "confined_space"
    BLIND_PLATE = "blind_plate"
    HEIGHT_WORK = "height_work"
    LIFTING = "lifting"
    TEMPORARY_ELECTRICITY = "temporary_electricity"
    EXCAVATION = "excavation"
    ROAD_BREAKING = "road_breaking"


OPERATION_TYPE_OPTIONS = [
    {"value": OperationType.HOT_WORK, "label": "动火作业"},
    {"value": OperationType.CONFINED_SPACE, "label": "受限空间作业"},
    {"value": OperationType.BLIND_PLATE, "label": "盲板抽堵作业"},
    {"value": OperationType.HEIGHT_WORK, "label": "高处作业"},
    {"value": OperationType.LIFTING, "label": "吊装作业"},
    {"value": OperationType.TEMPORARY_ELECTRICITY, "label": "临时用电作业"},
    {"value": OperationType.EXCAVATION, "label": "动土作业"},
    {"value": OperationType.ROAD_BREAKING, "label": "断路作业"},
]


class OperationLevel(str, Enum):
    """特殊作业级别枚举"""

    SPECIAL = "special"
    GRADE1 = "grade1"
    GRADE2 = "grade2"
    NOT_APPLICABLE = "not_applicable"


OPERATION_LEVEL_OPTIONS = [
    {"value": OperationLevel.SPECIAL, "label": "特级"},
    {"value": OperationLevel.GRADE1, "label": "一级"},
    {"value": OperationLevel.GRADE2, "label": "二级"},
    {"value": OperationLevel.NOT_APPLICABLE, "label": "不涉及"},
]


class PersonnelStatus(str, Enum):
    """人员资质状态枚举"""

    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"


PERSONNEL_STATUS_OPTIONS = [
    {"value": PersonnelStatus.ACTIVE, "label": "有效"},
    {"value": PersonnelStatus.EXPIRED, "label": "已过期"},
    {"value": PersonnelStatus.REVOKED, "label": "已撤销"},
]


class PermitStatus(str, Enum):
    """作业票状态枚举"""

    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


PERMIT_STATUS_OPTIONS = [
    {"value": PermitStatus.DRAFT, "label": "草稿"},
    {"value": PermitStatus.SUBMITTED, "label": "已提交"},
    {"value": PermitStatus.APPROVED, "label": "已审批"},
    {"value": PermitStatus.REJECTED, "label": "已驳回"},
    {"value": PermitStatus.IN_PROGRESS, "label": "作业中"},
    {"value": PermitStatus.COMPLETED, "label": "已完工"},
    {"value": PermitStatus.ARCHIVED, "label": "已归档"},
]


class CompletionMethod(str, Enum):
    """完工方式枚举"""

    NORMAL = "normal"
    EARLY_TERMINATION = "early_termination"


COMPLETION_METHOD_OPTIONS = [
    {"value": CompletionMethod.NORMAL, "label": "正常完工"},
    {"value": CompletionMethod.EARLY_TERMINATION, "label": "提前终止"},
]


class KnowledgeCategory(str, Enum):
    """安全知识库分类枚举"""

    LAWS_REGULATIONS = "laws_regulations"  # 法律法规
    STANDARDS = "standards"  # 标准规范
    MANAGEMENT_SYSTEMS = "management_systems"  # 管理制度
    ACCIDENT_CASES = "accident_cases"  # 事故案例
    EMERGENCY_PLANS = "emergency_plans"  # 应急预案
    SDS = "sds"  # 化学品安全技术说明书
    TRAINING_MATERIALS = "training_materials"  # 培训教材
    OTHER = "other"  # 其他


KNOWLEDGE_CATEGORY_OPTIONS = [
    {"value": KnowledgeCategory.LAWS_REGULATIONS, "label": "法律法规"},
    {"value": KnowledgeCategory.STANDARDS, "label": "标准规范"},
    {"value": KnowledgeCategory.MANAGEMENT_SYSTEMS, "label": "管理制度"},
    {"value": KnowledgeCategory.ACCIDENT_CASES, "label": "事故案例"},
    {"value": KnowledgeCategory.EMERGENCY_PLANS, "label": "应急预案"},
    {"value": KnowledgeCategory.SDS, "label": "化学品安全技术说明书"},
    {"value": KnowledgeCategory.TRAINING_MATERIALS, "label": "培训教材"},
    {"value": KnowledgeCategory.OTHER, "label": "其他"},
]


class DetectionTypeEnum(str, Enum):
    """检测类型枚举"""

    REGULAR = "regular"
    COMMISSIONED = "commissioned"
    EVALUATION = "evaluation"
    ACCIDENT = "accident"


DETECTION_TYPE_OPTIONS = [
    {"value": DetectionTypeEnum.REGULAR, "label": "定期检测"},
    {"value": DetectionTypeEnum.COMMISSIONED, "label": "委托检测"},
    {"value": DetectionTypeEnum.EVALUATION, "label": "评价检测"},
    {"value": DetectionTypeEnum.ACCIDENT, "label": "事故调查检测"},
]


class HazardFactorCategoryEnum(str, Enum):
    """危害因素类别枚举"""

    DUST = "dust"
    CHEMICAL = "chemical"
    PHYSICAL = "physical"


HAZARD_FACTOR_CATEGORY_OPTIONS = [
    {"value": HazardFactorCategoryEnum.DUST, "label": "粉尘（总尘/呼尘）"},
    {"value": HazardFactorCategoryEnum.CHEMICAL, "label": "化学物质"},
    {"value": HazardFactorCategoryEnum.PHYSICAL, "label": "物理因素"},
]


class OELComplianceStatusEnum(str, Enum):
    """OEL合规状态枚举"""

    COMPLIANT = "compliant"
    EXCEEDING = "exceeding"
    MARGINAL = "marginal"


OEL_COMPLIANCE_STATUS_OPTIONS = [
    {"value": OELComplianceStatusEnum.COMPLIANT, "label": "符合", "color": "green"},
    {"value": OELComplianceStatusEnum.EXCEEDING, "label": "超标", "color": "red"},
    {"value": OELComplianceStatusEnum.MARGINAL, "label": "临界", "color": "orange"},
]


class MonitorStatusEnum(str, Enum):
    """监测状态枚举"""

    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"


MONITOR_STATUS_OPTIONS = [
    {"value": MonitorStatusEnum.DRAFT, "label": "草稿", "color": "default"},
    {"value": MonitorStatusEnum.IN_PROGRESS, "label": "检测中", "color": "processing"},
    {"value": MonitorStatusEnum.COMPLETED, "label": "已完成", "color": "green"},
    {"value": MonitorStatusEnum.VERIFIED, "label": "已验证", "color": "cyan"},
]


class ExamTypeEnum(str, Enum):
    """体检类型枚举"""

    PRE_EMPLOYMENT = "pre_employment"
    PERIODIC = "periodic"
    POST_EMPLOYMENT = "post_employment"
    EMERGENCY = "emergency"


EXAM_TYPE_OPTIONS = [
    {"value": ExamTypeEnum.PRE_EMPLOYMENT, "label": "上岗前"},
    {"value": ExamTypeEnum.PERIODIC, "label": "在岗期间"},
    {"value": ExamTypeEnum.POST_EMPLOYMENT, "label": "离岗时"},
    {"value": ExamTypeEnum.EMERGENCY, "label": "应急/事故后"},
]


class ExamConclusionEnum(str, Enum):
    """体检结论枚举"""

    NORMAL = "normal"
    ABNORMAL_OTHER = "abnormal_other"
    SUSPECTED_OD = "suspected_od"
    OD_DIAGNOSED = "od_diagnosed"
    CONTRAINDICATED = "contraindicated"
    RE_EXAMINATION = "re_examination"


EXAM_CONCLUSION_OPTIONS = [
    {"value": ExamConclusionEnum.NORMAL, "label": "未见异常", "color": "green"},
    {"value": ExamConclusionEnum.ABNORMAL_OTHER, "label": "其他异常", "color": "orange"},
    {"value": ExamConclusionEnum.SUSPECTED_OD, "label": "疑似职业病", "color": "red"},
    {"value": ExamConclusionEnum.OD_DIAGNOSED, "label": "职业病确诊", "color": "red"},
    {"value": ExamConclusionEnum.CONTRAINDICATED, "label": "职业禁忌证", "color": "red"},
    {"value": ExamConclusionEnum.RE_EXAMINATION, "label": "复查", "color": "blue"},
]


class ExamStatusEnum(str, Enum):
    """体检状态枚举"""

    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


EXAM_STATUS_OPTIONS = [
    {"value": ExamStatusEnum.SCHEDULED, "label": "已安排", "color": "default"},
    {"value": ExamStatusEnum.IN_PROGRESS, "label": "体检中", "color": "processing"},
    {"value": ExamStatusEnum.COMPLETED, "label": "已完成", "color": "green"},
    {"value": ExamStatusEnum.ARCHIVED, "label": "已归档", "color": "default"},
]


class AbnormalityStatusEnum(str, Enum):
    """异常处置状态枚举"""

    OPEN = "open"
    INVESTIGATING = "investigating"
    CORRECTED = "corrected"
    CLOSED = "closed"


ABNORMALITY_STATUS_OPTIONS = [
    {"value": AbnormalityStatusEnum.OPEN, "label": "待处理", "color": "red"},
    {"value": AbnormalityStatusEnum.INVESTIGATING, "label": "调查中", "color": "orange"},
    {"value": AbnormalityStatusEnum.CORRECTED, "label": "已纠正", "color": "green"},
    {"value": AbnormalityStatusEnum.CLOSED, "label": "已关闭", "color": "default"},
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
    inspector_confirmed: bool = Field(False, description="检查人员确认")
    safety_officer_confirmed: bool = Field(False, description="安全办确认")
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
    inspector_confirmed: bool | None = Field(None, description="检查人员确认")
    safety_officer_confirmed: bool | None = Field(None, description="安全办确认")
    status: str | None = Field(None, max_length=32, description="状态")
    notes: str | None = Field(None, description="备注")


class SafetyCheckResponse(SafetyCheckBase):
    """安全检查响应"""

    id: uuid.UUID
    rectification_status: str | None = None
    inspector_confirmed: bool = False
    safety_officer_confirmed: bool = False
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 隐患排查 Schemas ====================


class CompleteRectificationRequest(BaseModel):
    """完成整改请求"""

    actual_completion_date: datetime | None = Field(None, description="实际完成时间")
    rectification_photos: str | None = Field(None, description="整改后图片JSON数组")
    corrective_preventive_measures: str | None = Field(None, description="纠正预防措施")


class RectificationReplyRequest(BaseModel):
    """整改回复请求"""

    reply_content: str = Field(..., description="整改回复内容")
    rectification_photos: str | None = Field(None, description="整改后图片JSON数组")


class VerifyLevelRequest(BaseModel):
    """三级复核请求"""

    level: int = Field(..., ge=1, le=3, description="复核级别: 1/2/3")
    action: str = Field(..., description="approved | rejected")
    opinion: str | None = Field(None, description="复核意见")


class ExtendDeadlineRequest(BaseModel):
    """延期请求"""

    extended_deadline: datetime = Field(..., description="延期至日期")


class ConfirmCheckRequest(BaseModel):
    """确认检查请求"""

    role: str = Field(..., description="确认角色: inspector / safety_officer")


class HazardReportBase(BaseModel):
    """隐患报告基础模式"""

    hazard_no: str = Field(..., max_length=64, description="隐患编号")
    inspection_category: str | None = Field(None, max_length=64, description="检查类别（日常检查/专项检查…）")
    hazard_type: HazardType = Field(..., description="隐患分类（人/物/环/管）")
    hazard_level: HazardLevel = Field(HazardLevel.GENERAL, description="隐患等级")
    hazard_category: HazardCategory | None = Field(None, description="隐患类别（设备设施/危化储存…）")
    description: str = Field(..., description="隐患描述")
    location: str | None = Field(None, max_length=255, description="地点/部位")
    discovered_by: uuid.UUID | None = Field(None, description="发现人")
    discovered_by_name: str | None = Field(None, max_length=100, description="发现人姓名")
    discovered_at: datetime = Field(..., description="发现时间")
    department: str | None = Field(None, max_length=100, description="责任部门")
    major_hazard_basis: str | None = Field(None, description="重大隐患判定依据")
    key_defect: str | None = Field(None, description="重点缺陷")
    defect_photos: str | None = Field(None, description="缺陷图片JSON数组")
    control_measures: str | None = Field(None, description="管控措施")
    rectification_responsible_person_name: str | None = Field(None, max_length=100, description="整改责任人姓名")
    rectification_responsible_department: str | None = Field(None, max_length=100, description="整改责任人部门")
    corrective_preventive_measures: str | None = Field(None, description="纠正预防措施")
    deadline: datetime | None = Field(None, description="计划完成时间")
    actual_completion_date: datetime | None = Field(None, description="实际完成时间")
    extended_deadline: datetime | None = Field(None, description="延期完成日期")
    rectification_photos: str | None = Field(None, description="整改后图片JSON数组")
    check_id: uuid.UUID | None = Field(None, description="关联检查ID")
    notes: str | None = Field(None, description="备注")


class HazardReportCreate(HazardReportBase):
    """创建隐患报告"""

    hazard_no: str | None = Field(None, max_length=64, description="隐患编号（留空自动生成）")
    hazard_type: HazardType | None = Field(None, description="隐患分类")
    hazard_level: HazardLevel | None = Field(None, description="隐患等级")
    hazard_category: HazardCategory | None = Field(None, description="隐患类别")
    description: str | None = Field(None, description="隐患描述")
    discovered_at: datetime | None = Field(None, description="发现时间")


class HazardReportUpdate(BaseModel):
    """更新隐患报告"""

    hazard_no: str | None = Field(None, max_length=64, description="隐患编号")
    inspection_category: str | None = Field(None, max_length=64, description="检查类别（日常检查/专项检查…）")
    hazard_type: HazardType | None = Field(None, description="隐患分类")
    hazard_level: HazardLevel | None = Field(None, description="隐患等级")
    hazard_category: HazardCategory | None = Field(None, description="隐患类别")
    description: str | None = Field(None, description="隐患描述")
    location: str | None = Field(None, max_length=255, description="地点/部位")
    department: str | None = Field(None, max_length=100, description="责任部门")
    major_hazard_basis: str | None = Field(None, description="重大隐患判定依据")
    key_defect: str | None = Field(None, description="重点缺陷")
    defect_photos: str | None = Field(None, description="缺陷图片JSON数组")
    control_measures: str | None = Field(None, description="管控措施")
    rectification_responsible_person_name: str | None = Field(None, max_length=100, description="整改责任人姓名")
    rectification_responsible_department: str | None = Field(None, max_length=100, description="整改责任人部门")
    corrective_preventive_measures: str | None = Field(None, description="纠正预防措施")
    deadline: datetime | None = Field(None, description="计划完成时间")
    actual_completion_date: datetime | None = Field(None, description="实际完成时间")
    extended_deadline: datetime | None = Field(None, description="延期完成日期")
    rectification_photos: str | None = Field(None, description="整改后图片JSON数组")
    rectification_status: str | None = Field(None, max_length=32, description="整改进度")
    # ── 整改回复 ──
    rectification_reply: str | None = Field(None, description="整改回复内容")
    rectification_replied_at: datetime | None = Field(None, description="整改回复时间")
    rectification_replied_by: uuid.UUID | None = Field(None, description="整改回复人ID")
    rectification_replied_by_name: str | None = Field(None, max_length=100, description="整改回复人姓名")
    # ── 三级复核 ──
    verify_level_1_status: str | None = Field(None, max_length=20, description="一级复核状态")
    verify_level_1_by: uuid.UUID | None = Field(None, description="一级复核人ID")
    verify_level_1_by_name: str | None = Field(None, max_length=100, description="一级复核人姓名")
    verify_level_1_at: datetime | None = Field(None, description="一级复核时间")
    verify_level_1_opinion: str | None = Field(None, description="一级复核意见")
    verify_level_2_status: str | None = Field(None, max_length=20, description="二级复核状态")
    verify_level_2_by: uuid.UUID | None = Field(None, description="二级复核人ID")
    verify_level_2_by_name: str | None = Field(None, max_length=100, description="二级复核人姓名")
    verify_level_2_at: datetime | None = Field(None, description="二级复核时间")
    verify_level_2_opinion: str | None = Field(None, description="二级复核意见")
    verify_level_3_status: str | None = Field(None, max_length=20, description="三级复核状态")
    verify_level_3_by: uuid.UUID | None = Field(None, description="三级复核人ID")
    verify_level_3_by_name: str | None = Field(None, max_length=100, description="三级复核人姓名")
    verify_level_3_at: datetime | None = Field(None, description="三级复核时间")
    verify_level_3_opinion: str | None = Field(None, description="三级复核意见")
    verified_by: uuid.UUID | None = Field(None, description="验证人")
    verified_by_name: str | None = Field(None, max_length=100, description="验证人姓名")
    verified_at: datetime | None = Field(None, description="验证时间")
    status: str | None = Field(None, max_length=32, description="状态")
    notes: str | None = Field(None, description="备注")
    # ── AI 流程字段 ──
    ai_node_progress: str | None = Field(None, max_length=50, description="AI流程节点进度")
    overall_status: str | None = Field(None, max_length=20, description="整体状态")
    ai_error_message: str | None = Field(None, description="AI错误信息")
    script1_review_status: str | None = Field(None, max_length=20, description="AI隐患识别审核状态")
    script2_review_status: str | None = Field(None, max_length=20, description="AI整改建议审核状态")


class HazardReportResponse(HazardReportBase):
    """隐患报告响应"""

    id: uuid.UUID
    rectification_status: str
    status: str
    verified_by: uuid.UUID | None = None
    verified_by_name: str | None = None
    verified_at: datetime | None = None
    # ── 整改回复 ──
    rectification_reply: str | None = None
    rectification_replied_at: datetime | None = None
    rectification_replied_by: uuid.UUID | None = None
    rectification_replied_by_name: str | None = None
    # ── 三级复核 ──
    verify_level_1_status: str = "pending"
    verify_level_1_by: uuid.UUID | None = None
    verify_level_1_by_name: str | None = None
    verify_level_1_at: datetime | None = None
    verify_level_1_opinion: str | None = None
    verify_level_2_status: str = "pending"
    verify_level_2_by: uuid.UUID | None = None
    verify_level_2_by_name: str | None = None
    verify_level_2_at: datetime | None = None
    verify_level_2_opinion: str | None = None
    verify_level_3_status: str = "pending"
    verify_level_3_by: uuid.UUID | None = None
    verify_level_3_by_name: str | None = None
    verify_level_3_at: datetime | None = None
    verify_level_3_opinion: str | None = None
    # ── AI 流程字段 ──
    ai_node_progress: str = "pending_input"
    overall_status: str = "draft"
    ai_error_message: str | None = None
    script1_review_status: str = "pending"
    script2_review_status: str = "pending"
    ai_generated: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HazardReportRunAIRequest(BaseModel):
    """执行隐患AI工作流请求（AI从已有数据读取上下文）"""

    pass


# ==================== 事故管理 Schemas ====================


class AccidentBase(BaseModel):
    """事故基础模式"""

    accident_no: str = Field(..., max_length=64, description="事故编号")
    accident_type: AccidentType = Field(..., description="事故类型")
    accident_level: AccidentLevel = Field(AccidentLevel.GENERAL, description="事故等级")
    happened_at: datetime = Field(..., description="发生时间")
    location: str | None = Field(None, max_length=255, description="发生地点")
    department: str | None = Field(None, max_length=100, description="发生部门")
    description: str = Field(..., description="事故描述")
    casualties: str | None = Field(None, max_length=255, description="伤亡情况汇总")
    property_damage: float | None = Field(None, ge=0, description="财产损失(元)")
    loss_work_days: int | None = Field(None, ge=0, description="损失工作日")
    injury_details: list | None = Field(None, description="伤员详情")
    investigation_team: list | None = Field(None, description="调查组")
    investigation_method: str | None = Field(None, max_length=100, description="调查方法")
    investigation_findings: str | None = Field(None, description="调查发现")
    investigation_report_path: str | None = Field(None, max_length=500, description="调查报告文件路径")
    direct_cause: str | None = Field(None, description="直接原因")
    root_cause: str | None = Field(None, description="根本原因")
    handling_measures: str | None = Field(None, description="处理措施")
    corrective_actions: str | None = Field(None, description="纠正预防措施")
    corrective_action_deadline: datetime | None = Field(None, description="CAPA截止日期")
    corrective_action_responsible: str | None = Field(None, max_length=100, description="CAPA责任人")
    corrective_action_status: str | None = Field(None, max_length=32, description="CAPA状态")
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
    department: str | None = Field(None, max_length=100, description="发生部门")
    description: str | None = Field(None, description="事故描述")
    casualties: str | None = Field(None, max_length=255, description="伤亡情况汇总")
    property_damage: float | None = Field(None, ge=0, description="财产损失(元)")
    loss_work_days: int | None = Field(None, ge=0, description="损失工作日")
    injury_details: list | None = Field(None, description="伤员详情")
    investigation_team: list | None = Field(None, description="调查组")
    investigation_method: str | None = Field(None, max_length=100, description="调查方法")
    investigation_findings: str | None = Field(None, description="调查发现")
    investigation_report_path: str | None = Field(None, max_length=500, description="调查报告文件路径")
    direct_cause: str | None = Field(None, description="直接原因")
    root_cause: str | None = Field(None, description="根本原因")
    handling_measures: str | None = Field(None, description="处理措施")
    corrective_actions: str | None = Field(None, description="纠正预防措施")
    corrective_action_deadline: datetime | None = Field(None, description="CAPA截止日期")
    corrective_action_responsible: str | None = Field(None, max_length=100, description="CAPA责任人")
    corrective_action_status: str | None = Field(None, max_length=32, description="CAPA状态")
    status: str | None = Field(None, max_length=32, description="状态")
    investigator: uuid.UUID | None = Field(None, description="调查人")
    investigator_name: str | None = Field(None, max_length=100, description="调查人姓名")
    verified_by: uuid.UUID | None = Field(None, description="CAPA验证人")
    verified_by_name: str | None = Field(None, max_length=100, description="验证人姓名")
    verified_at: datetime | None = Field(None, description="验证时间")
    notes: str | None = Field(None, description="备注")


class AccidentResponse(AccidentBase):
    """事故响应"""

    id: uuid.UUID
    status: str
    investigator: uuid.UUID | None = None
    investigator_name: str | None = None
    verified_by: uuid.UUID | None = None
    verified_by_name: str | None = None
    verified_at: datetime | None = None
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
    training_level: TrainingLevel = Field(TrainingLevel.DEPT, description="培训级别")
    trainer: uuid.UUID | None = Field(None, description="培训讲师")
    trainer_name: str | None = Field(None, max_length=100, description="讲师姓名")
    training_date: datetime = Field(..., description="培训日期")
    duration_hours: float | None = Field(None, ge=0, description="培训时长(小时)")
    location: str | None = Field(None, max_length=255, description="培训地点")
    content: str | None = Field(None, description="培训内容")
    department: str | None = Field(None, max_length=100, description="培训部门")
    exam_passing_score: float | None = Field(60, ge=0, description="及格分数线")
    course_material_path: str | None = Field(None, max_length=500, description="课程资料路径")
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
    position: str | None = Field(None, max_length=100, description="岗位")
    attendance: bool = Field(True, description="是否出席")
    score: float | None = Field(None, ge=0, le=100, description="考核成绩")
    passed: bool | None = Field(None, description="是否合格")
    certificate_no: str | None = Field(None, max_length=100, description="证书编号")
    certificate_expiry: datetime | None = Field(None, description="证书有效期至")
    certificate_status: str | None = Field(None, max_length=32, description="证书状态")
    certificate_file_path: str | None = Field(None, max_length=500, description="证书文件路径")
    notes: str | None = Field(None, description="备注")


class TrainingRecordCreate(TrainingRecordBase):
    """创建培训记录"""

    training_id: uuid.UUID


class TrainingRecordUpdate(BaseModel):
    """更新培训记录"""

    employee_id: uuid.UUID | None = Field(None, description="员工ID")
    employee_name: str | None = Field(None, max_length=100, description="员工姓名")
    department: str | None = Field(None, max_length=100, description="部门")
    position: str | None = Field(None, max_length=100, description="岗位")
    attendance: bool | None = Field(None, description="是否出席")
    score: float | None = Field(None, ge=0, le=100, description="考核成绩")
    passed: bool | None = Field(None, description="是否合格")
    certificate_no: str | None = Field(None, max_length=100, description="证书编号")
    certificate_expiry: datetime | None = Field(None, description="证书有效期至")
    certificate_status: str | None = Field(None, max_length=32, description="证书状态")
    certificate_file_path: str | None = Field(None, max_length=500, description="证书文件路径")
    notes: str | None = Field(None, description="备注")


class TrainingRecordResponse(TrainingRecordBase):
    """培训记录响应"""

    id: uuid.UUID
    training_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 危险源辨识 ====================


# ── 风险等级常量 ──
RISK_LEVELS = [
    {"key": "level_1", "label": "一级/重大风险", "min_d": 320, "max_d": 99999, "color": "red",
     "control_level": "公司级", "responsible_person": "公司主要负责人",
     "requirement": "必须建立管控档案，立即整改，风险降低后方可作业"},
    {"key": "level_2", "label": "二级/较大风险", "min_d": 160, "max_d": 319, "color": "orange",
     "control_level": "部门级", "responsible_person": "安全工程中心 + 各部门按职责分工",
     "requirement": "必须建立管控档案，制定措施控制管理"},
    {"key": "level_3", "label": "三级/一般风险", "min_d": 70, "max_d": 159, "color": "yellow",
     "control_level": "班组/岗位级", "responsible_person": "所在部门负责管控",
     "requirement": "安全工程中心监督落实"},
    {"key": "level_4", "label": "四级/低风险", "min_d": 0, "max_d": 69, "color": "blue",
     "control_level": "班组/岗位级", "responsible_person": "所在班组/岗位负责管控",
     "requirement": "部门安全员监督落实"},
]


def get_risk_level(d_value: float) -> dict:
    """根据 D 值获取风险等级"""
    for level in RISK_LEVELS:
        if level["min_d"] <= d_value <= level["max_d"]:
            return level
    return RISK_LEVELS[-1]


AI_NODE_PROGRESS_OPTIONS = [
    {"value": "pending_input", "label": "待填写基础信息"},
    {"value": "pending_script1", "label": "待AI解析附件"},
    {"value": "pending_script2", "label": "待AI危险源辨识"},
    {"value": "pending_script3", "label": "待AI固有风险评价"},
    {"value": "pending_script4", "label": "待AI输入现有控制措施"},
    {"value": "pending_script5", "label": "待AI评价残余风险"},
    {"value": "pending_script6", "label": "待AI提出建议措施"},
    {"value": "pending_script7", "label": "待AI评价建议措施后风险"},
    {"value": "completed", "label": "AI流程结束"},
]

REVIEW_STATUS_OPTIONS = [
    {"value": "pending", "label": "待审核"},
    {"value": "approved", "label": "已审核"},
    {"value": "rejected", "label": "已驳回"},
]

OVERALL_STATUS_OPTIONS = [
    {"value": "draft", "label": "草稿"},
    {"value": "in_progress", "label": "进行中"},
    {"value": "completed", "label": "已完成"},
    {"value": "cancelled", "label": "已取消"},
]


class HazardIdentificationBase(BaseModel):
    """危险源辨识基础模式"""

    hazard_id_no: str = Field(..., max_length=64, description="危险源编号")
    department: str = Field(..., max_length=100, description="部门")
    position: str = Field(..., max_length=100, description="岗位")
    production_step: str = Field(..., description="生产步骤")
    notes: str | None = Field(None, description="备注")


class HazardIdentificationCreate(HazardIdentificationBase):
    """创建危险源辨识记录"""
    pass


class HazardIdentificationUpdate(BaseModel):
    """更新危险源辨识记录（人工编辑字段）"""
    hazard_id_no: str | None = Field(None, max_length=64)
    department: str | None = Field(None, max_length=100)
    position: str | None = Field(None, max_length=100)
    production_step: str | None = None
    notes: str | None = None
    specific_activity: str | None = None
    equipment_facilities: str | None = None
    raw_auxiliary_materials: str | None = None
    operation_frequency: str | None = None
    operator_count: int | None = None
    hazard_type: str | None = None
    possible_accident: str | None = None
    unsafe_behavior: str | None = None
    l_inherent: float | None = None
    e_inherent: float | None = None
    c_inherent: float | None = None
    d_inherent: float | None = None
    inherent_risk_level: str | None = None
    inherent_risk_label: str | None = None
    existing_engineering_controls: str | None = None
    existing_management_controls: str | None = None
    existing_ppe: str | None = None
    existing_emergency_measures: str | None = None
    l_residual: float | None = None
    e_residual: float | None = None
    c_residual: float | None = None
    d_residual: float | None = None
    residual_risk_level: str | None = None
    residual_risk_label: str | None = None
    needs_recommendation: str | None = None
    recommendation_type: str | None = None
    recommendation_content: str | None = None
    recommendation_priority: str | None = None
    l_post: float | None = None
    e_post: float | None = None
    c_post: float | None = None
    d_post: float | None = None
    post_risk_level: str | None = None
    post_risk_label: str | None = None


class HazardIdentificationReview(BaseModel):
    """审核请求"""
    script_number: int = Field(..., ge=1, le=7, description="脚本编号(1-7)")
    action: str = Field(..., description="审核动作: approved/rejected")


class HazardIdentificationRunScript(BaseModel):
    """触发脚本执行请求"""
    script_number: int = Field(..., ge=1, le=7, description="脚本编号(1-7)")
    ai_output: dict | None = Field(None, description="AI 输出内容")


class HazardIdentificationResponse(HazardIdentificationBase):
    """危险源辨识完整响应"""

    id: uuid.UUID
    attachment_path: str | None = None
    attachment_original_name: str | None = None
    specific_activity: str | None = None
    equipment_facilities: str | None = None
    raw_auxiliary_materials: str | None = None
    operation_frequency: str | None = None
    operator_count: int | None = None
    hazard_type: str | None = None
    possible_accident: str | None = None
    unsafe_behavior: str | None = None
    l_inherent: float | None = None
    e_inherent: float | None = None
    c_inherent: float | None = None
    d_inherent: float | None = None
    inherent_risk_level: str | None = None
    inherent_risk_label: str | None = None
    existing_engineering_controls: str | None = None
    existing_management_controls: str | None = None
    existing_ppe: str | None = None
    existing_emergency_measures: str | None = None
    l_residual: float | None = None
    e_residual: float | None = None
    c_residual: float | None = None
    d_residual: float | None = None
    residual_risk_level: str | None = None
    residual_risk_label: str | None = None
    needs_recommendation: str | None = None
    recommendation_type: str | None = None
    recommendation_content: str | None = None
    recommendation_priority: str | None = None
    l_post: float | None = None
    e_post: float | None = None
    c_post: float | None = None
    d_post: float | None = None
    post_risk_level: str | None = None
    post_risk_label: str | None = None
    control_level: str | None = None
    responsible_person: str | None = None
    ai_node_progress: str
    ai_error_message: str | None = None
    overall_status: str
    script1_review_status: str
    script2_review_status: str
    script3_review_status: str
    script4_review_status: str
    script5_review_status: str
    script6_review_status: str
    script7_review_status: str
    created_by: uuid.UUID | None = None
    updated_by: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 安全操作规程 Schemas ====================


class OperationRegulationBase(BaseModel):
    """安全操作规程基础模式"""

    regulation_no: str = Field(..., max_length=64, description="操规编号")
    regulation_name: str = Field(..., max_length=255, description="操规名称")
    document_path: str | None = Field(None, max_length=500, description="操规文档路径")
    document_original_name: str | None = Field(None, max_length=255, description="文档原始文件名")
    position: str | None = Field(None, max_length=100, description="岗位（达托/达巴，逗号分隔）")
    notes: str | None = Field(None, description="备注")


class OperationRegulationCreate(OperationRegulationBase):
    """创建安全操作规程"""
    pass


class OperationRegulationUpdate(BaseModel):
    """更新安全操作规程"""
    regulation_no: str | None = Field(None, max_length=64, description="操规编号")
    regulation_name: str | None = Field(None, max_length=255, description="操规名称")
    document_path: str | None = Field(None, max_length=500, description="操规文档路径")
    document_original_name: str | None = Field(None, max_length=255, description="文档原始文件名")
    position: str | None = Field(None, max_length=100, description="岗位")
    notes: str | None = Field(None, description="备注")


class OperationRegulationResponse(OperationRegulationBase):
    """安全操作规程响应"""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 操规修订记录 Schemas ====================


class RegulationRevisionBase(BaseModel):
    """修订记录基础模式"""
    revision_no: str = Field(..., max_length=64, description="修订编号")
    regulation_id: uuid.UUID = Field(..., description="关联操规ID")
    regulation_name: str = Field(..., max_length=255, description="安全操规名称")
    old_document_path: str | None = Field(None, max_length=500, description="旧文档路径")
    reviser: uuid.UUID | None = Field(None, description="修订人")
    reviser_name: str | None = Field(None, max_length=100, description="修订人姓名")
    revision_time: datetime = Field(..., description="修订时间")
    revision_type: RevisionType = Field(RevisionType.MANUAL, description="修订类型")
    revision_opinion: str | None = Field(None, description="修订意见/内容")
    revision_scope: str | None = Field(None, max_length=100, description="修订范围")
    new_document_path: str | None = Field(None, max_length=500, description="新文档路径")
    notes: str | None = Field(None, description="备注")


class RegulationRevisionCreate(BaseModel):
    """创建修订记录"""
    revision_no: str = Field(..., max_length=64, description="修订编号")
    regulation_id: uuid.UUID = Field(..., description="关联操规ID")
    revision_type: RevisionType = Field(RevisionType.MANUAL, description="修订类型")
    revision_opinion: str | None = Field(None, description="修订意见/内容")
    reviser: uuid.UUID | None = Field(None, description="修订人")
    reviser_name: str | None = Field(None, max_length=100, description="修订人姓名")
    notes: str | None = Field(None, description="备注")


class RegulationRevisionUpdate(BaseModel):
    """更新修订记录"""
    revision_opinion: str | None = Field(None, description="修订意见/内容")
    revision_scope: str | None = Field(None, max_length=100, description="修订范围")
    review_opinion: str | None = Field(None, max_length=32, description="审核意见")
    new_document_path: str | None = Field(None, max_length=500, description="新文档路径")
    notes: str | None = Field(None, description="备注")


class RegulationRevisionAIDiff(BaseModel):
    """AI 差异识别请求"""
    old_content: str | None = Field(None, description="旧文档内容")
    new_content: str = Field(..., description="新文档内容（修订人发送的）")


class RegulationRevisionAIGenerate(BaseModel):
    """AI 生成修订版本请求"""
    regulation_name: str = Field(..., description="操规名称")
    current_content: str = Field(..., description="当前操规内容")
    revision_opinion: str = Field(..., description="修订意见")


class RegulationRevisionResponse(RegulationRevisionBase):
    """修订记录响应"""
    id: uuid.UUID
    review_opinion: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 修订范围 AI 识别 Schemas ====================


class RevisionScopeIdentifyRequest(BaseModel):
    """AI 识别修订范围请求"""
    revision_opinion: str = Field(..., description="修订意见内容")
    revision_type: RevisionType = Field(..., description="修订类型")


class RevisionScopeIdentifyResponse(BaseModel):
    """AI 识别修订范围响应"""
    scope: str = Field(..., description="识别的修订范围（逗号分隔: process/safety_requirement）")
    reasoning: str = Field(..., description="识别依据说明")


# ==================== AI 工作流配置 Schemas ====================


class AIWorkflowConfigBase(BaseModel):
    """AI 工作流配置基础模式"""

    module_code: str = Field(..., max_length=64, description="模块代码")
    workflow_name: str = Field(..., max_length=128, description="工作流名称")
    workflow_description: str | None = Field(None, description="工作流描述")
    trigger_event: str | None = Field(None, max_length=64, description="触发事件")
    is_enabled: bool = Field(True, description="是否启用")
    script_configs: list[dict] | dict | None = Field(None, description="脚本配置 JSON")
    sort_order: int = Field(0, description="排序顺序")
    notes: str | None = Field(None, description="备注")


class AIWorkflowConfigCreate(BaseModel):
    """创建 AI 工作流配置"""
    module_code: str = Field(..., max_length=64, description="模块代码")
    workflow_name: str = Field(..., max_length=128, description="工作流名称")
    workflow_description: str | None = Field(None, description="工作流描述")
    trigger_event: str | None = Field(None, max_length=64, description="触发事件")
    is_enabled: bool = Field(True, description="是否启用")
    script_configs: list[dict] | dict | None = Field(None, description="脚本配置 JSON")
    sort_order: int = Field(0, description="排序顺序")
    notes: str | None = Field(None, description="备注")


class AIWorkflowConfigUpdate(BaseModel):
    """更新 AI 工作流配置"""
    module_code: str | None = Field(None, max_length=64, description="模块代码")
    workflow_name: str | None = Field(None, max_length=128, description="工作流名称")
    workflow_description: str | None = Field(None, description="工作流描述")
    trigger_event: str | None = Field(None, max_length=64, description="触发事件")
    is_enabled: bool | None = Field(None, description="是否启用")
    script_configs: list[dict] | dict | None = Field(None, description="脚本配置 JSON")
    sort_order: int | None = Field(None, description="排序顺序")
    notes: str | None = Field(None, description="备注")


class AIWorkflowConfigResponse(AIWorkflowConfigBase):
    """AI 工作流配置响应"""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== API 调用配置 Schemas ====================


class APICallConfigBase(BaseModel):
    """API 调用配置基础模式"""

    config_name: str = Field(..., max_length=128, description="配置名称")
    config_type: str = Field("text", max_length=20, description="配置类型: text(文本模型) / vision(视觉模型)")
    api_base_url: str = Field(..., max_length=500, description="API 基础 URL")
    api_key: str = Field(..., max_length=500, description="API 密钥")
    model_name: str = Field(..., max_length=128, description="模型名称")
    temperature: float = Field(0.1, description="温度参数")
    timeout_seconds: int = Field(120, description="超时秒数")
    max_tokens: int | None = Field(None, description="最大 Token 数")
    extra_config: dict | None = Field(None, description="额外配置 JSON")
    is_active: bool = Field(False, description="是否激活")
    notes: str | None = Field(None, description="备注")


class APICallConfigCreate(BaseModel):
    """创建 API 调用配置"""
    config_name: str = Field(..., max_length=128, description="配置名称")
    config_type: str = Field("text", max_length=20, description="配置类型: text(文本模型) / vision(视觉模型)")
    api_base_url: str = Field(..., max_length=500, description="API 基础 URL")
    api_key: str = Field(..., max_length=500, description="API 密钥")
    model_name: str = Field(..., max_length=128, description="模型名称")
    temperature: float = Field(0.1, description="温度参数")
    timeout_seconds: int = Field(120, description="超时秒数")
    max_tokens: int | None = Field(None, description="最大 Token 数")
    extra_config: dict | None = Field(None, description="额外配置 JSON")
    is_active: bool = Field(False, description="是否激活")
    notes: str | None = Field(None, description="备注")


class APICallConfigUpdate(BaseModel):
    """更新 API 调用配置"""
    config_name: str | None = Field(None, max_length=128, description="配置名称")
    config_type: str | None = Field(None, max_length=20, description="配置类型: text(文本模型) / vision(视觉模型)")
    api_base_url: str | None = Field(None, max_length=500, description="API 基础 URL")
    api_key: str | None = Field(None, max_length=500, description="API 密钥")
    model_name: str | None = Field(None, max_length=128, description="模型名称")
    temperature: float | None = Field(None, description="温度参数")
    timeout_seconds: int | None = Field(None, description="超时秒数")
    max_tokens: int | None = Field(None, description="最大 Token 数")
    extra_config: dict | None = Field(None, description="额外配置 JSON")
    is_active: bool | None = Field(None, description="是否激活")
    notes: str | None = Field(None, description="备注")


class APICallConfigResponse(APICallConfigBase):
    """API 调用配置响应"""
    id: uuid.UUID
    source: str = Field("db", description="配置来源: db(数据库) / env(环境变量)")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 特殊作业人员资质 Schemas ====================


class SpecialOperationPersonnelBase(BaseModel):
    """特殊作业人员资质基础模式"""

    personnel_no: str = Field(..., max_length=64, description="人员编号")
    name: str = Field(..., max_length=100, description="姓名")
    department: str | None = Field(None, max_length=100, description="所属部门")
    certificate_type: OperationType = Field(..., description="证书类型")
    certificate_number: str | None = Field(None, max_length=100, description="证书编号")
    issuing_authority: str | None = Field(None, max_length=200, description="发证机关")
    issue_date: datetime | None = Field(None, description="发证日期")
    expiry_date: datetime | None = Field(None, description="有效期至")
    certificate_file_path: str | None = Field(None, max_length=500, description="证书文件路径")
    qualification_scope: str | None = Field(None, description="资质范围")
    notes: str | None = Field(None, description="备注")


class SpecialOperationPersonnelCreate(SpecialOperationPersonnelBase):
    """创建人员资质"""
    pass


class SpecialOperationPersonnelUpdate(BaseModel):
    """更新人员资质"""

    personnel_no: str | None = Field(None, max_length=64, description="人员编号")
    name: str | None = Field(None, max_length=100, description="姓名")
    department: str | None = Field(None, max_length=100, description="所属部门")
    certificate_type: OperationType | None = Field(None, description="证书类型")
    certificate_number: str | None = Field(None, max_length=100, description="证书编号")
    issuing_authority: str | None = Field(None, max_length=200, description="发证机关")
    issue_date: datetime | None = Field(None, description="发证日期")
    expiry_date: datetime | None = Field(None, description="有效期至")
    certificate_file_path: str | None = Field(None, max_length=500, description="证书文件路径")
    qualification_scope: str | None = Field(None, description="资质范围")
    status: PersonnelStatus | None = Field(None, description="状态")
    notes: str | None = Field(None, description="备注")


class SpecialOperationPersonnelResponse(SpecialOperationPersonnelBase):
    """人员资质响应"""

    id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 特殊作业票 Schemas ====================


class SpecialOperationPermitBase(BaseModel):
    """特殊作业票基础模式"""

    permit_no: str = Field(..., max_length=64, description="作业票编号")
    operation_type: OperationType = Field(..., description="作业类型")
    operation_level: OperationLevel = Field(OperationLevel.GRADE2, description="作业级别")
    location: str | None = Field(None, max_length=255, description="作业地点")
    equipment_tag: str | None = Field(None, max_length=100, description="设备位号")
    work_description: str | None = Field(None, description="作业内容描述")
    planned_start_time: datetime | None = Field(None, description="计划开始时间")
    planned_end_time: datetime | None = Field(None, description="计划结束时间")
    actual_start_time: datetime | None = Field(None, description="实际开始时间")
    actual_end_time: datetime | None = Field(None, description="实际结束时间")
    applicant_name: str | None = Field(None, max_length=100, description="申请人姓名")
    work_leader_name: str | None = Field(None, max_length=100, description="作业负责人姓名")
    operator_names: str | None = Field(None, description="作业人员姓名")
    guardian_name: str | None = Field(None, max_length=100, description="监护人姓名")
    approver_name: str | None = Field(None, max_length=100, description="审批人姓名")
    safety_measures: str | None = Field(None, description="安全措施")
    emergency_equipment: str | None = Field(None, description="应急消防器材")
    gas_analysis: str | None = Field(None, description="气体分析结果")
    risk_assessment: str | None = Field(None, description="风险评估")
    check_id: uuid.UUID | None = Field(None, description="关联安全检查ID")
    notes: str | None = Field(None, description="备注")


class SpecialOperationPermitCreate(SpecialOperationPermitBase):
    """创建作业票"""
    pass


class SpecialOperationPermitUpdate(BaseModel):
    """更新作业票"""

    permit_no: str | None = Field(None, max_length=64, description="作业票编号")
    operation_type: OperationType | None = Field(None, description="作业类型")
    operation_level: OperationLevel | None = Field(None, description="作业级别")
    location: str | None = Field(None, max_length=255, description="作业地点")
    equipment_tag: str | None = Field(None, max_length=100, description="设备位号")
    work_description: str | None = Field(None, description="作业内容描述")
    planned_start_time: datetime | None = Field(None, description="计划开始时间")
    planned_end_time: datetime | None = Field(None, description="计划结束时间")
    actual_start_time: datetime | None = Field(None, description="实际开始时间")
    actual_end_time: datetime | None = Field(None, description="实际结束时间")
    applicant_name: str | None = Field(None, max_length=100, description="申请人姓名")
    work_leader_name: str | None = Field(None, max_length=100, description="作业负责人姓名")
    operator_names: str | None = Field(None, description="作业人员姓名")
    guardian_name: str | None = Field(None, max_length=100, description="监护人姓名")
    approver_name: str | None = Field(None, max_length=100, description="审批人姓名")
    safety_measures: str | None = Field(None, description="安全措施")
    emergency_equipment: str | None = Field(None, description="应急消防器材")
    gas_analysis: str | None = Field(None, description="气体分析结果")
    risk_assessment: str | None = Field(None, description="风险评估")
    safety_briefing_confirmed: bool | None = Field(None, description="安全交底确认")
    safety_briefing_time: datetime | None = Field(None, description="安全交底时间")
    rejection_reason: str | None = Field(None, description="驳回原因")
    completion_method: CompletionMethod | None = Field(None, description="完工方式")
    status: PermitStatus | None = Field(None, description="状态")
    check_id: uuid.UUID | None = Field(None, description="关联安全检查ID")
    notes: str | None = Field(None, description="备注")


class SpecialOperationPermitResponse(SpecialOperationPermitBase):
    """作业票响应"""

    id: uuid.UUID
    safety_briefing_confirmed: bool = False
    safety_briefing_time: datetime | None = None
    rejection_reason: str | None = None
    completion_method: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 安全知识库 Schemas ====================


class SafetyKnowledgeArticleBase(BaseModel):
    """安全知识库文章基础模式"""

    title: str = Field(..., max_length=255, description="文章标题")
    summary: str | None = Field(None, description="摘要")
    content: str | None = Field(None, description="正文内容")
    tags: str | None = Field(None, max_length=500, description="标签（逗号分隔）")
    category: KnowledgeCategory = Field(KnowledgeCategory.OTHER, description="分类")


class SafetyKnowledgeArticleCreate(SafetyKnowledgeArticleBase):
    """创建知识库文章"""

    pass


class SafetyKnowledgeArticleUpdate(BaseModel):
    """更新知识库文章"""

    title: str | None = Field(None, max_length=255, description="文章标题")
    summary: str | None = Field(None, description="摘要")
    content: str | None = Field(None, description="正文内容")
    tags: str | None = Field(None, max_length=500, description="标签（逗号分隔）")
    category: KnowledgeCategory | None = Field(None, description="分类")
    status: str | None = Field(None, max_length=32, description="状态")


class SafetyKnowledgeArticleResponse(SafetyKnowledgeArticleBase):
    """安全知识库文章响应"""

    id: uuid.UUID
    status: str
    view_count: int = 0
    attachment_path: str | None = None
    attachment_original_name: str | None = None
    created_by: uuid.UUID | None = None
    updated_by: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 风险作业报备 Schemas ====================


class ReportStatus(str, Enum):
    """报备状态枚举"""

    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"


REPORT_STATUS_OPTIONS = [
    {"value": ReportStatus.DRAFT, "label": "草稿"},
    {"value": ReportStatus.SUBMITTED, "label": "已提交"},
    {"value": ReportStatus.APPROVED, "label": "已审批"},
    {"value": ReportStatus.REJECTED, "label": "已驳回"},
]


# ── 八大特殊作业报备 ──


class SpecialOperationReportBase(BaseModel):
    """特殊作业报备基础模式"""

    report_no: str = Field(..., max_length=64, description="报备编号")
    permit_id: uuid.UUID | None = Field(None, description="关联作业票ID")
    operation_type: OperationType = Field(..., description="作业类型")
    operation_level: OperationLevel = Field(OperationLevel.GRADE2, description="作业级别")
    department: str | None = Field(None, max_length=100, description="报备部门")
    location: str | None = Field(None, max_length=255, description="作业地点")
    equipment_tag: str | None = Field(None, max_length=100, description="设备位号")
    work_description: str | None = Field(None, description="作业内容描述")
    planned_start_time: datetime | None = Field(None, description="计划开始时间")
    planned_end_time: datetime | None = Field(None, description="计划结束时间")
    work_leader_name: str | None = Field(None, max_length=100, description="作业负责人姓名")
    operator_names: str | None = Field(None, description="作业人员姓名（逗号分隔）")
    guardian_name: str | None = Field(None, max_length=100, description="监护人姓名")
    risk_level: str | None = Field(None, max_length=20, description="风险等级")
    safety_measures: str | None = Field(None, description="安全措施")
    emergency_equipment: str | None = Field(None, description="应急消防器材")
    gas_analysis: str | None = Field(None, description="气体分析结果")
    risk_assessment: str | None = Field(None, description="风险评估描述")
    applicant_name: str | None = Field(None, max_length=100, description="报备申请人姓名")
    approver_name: str | None = Field(None, max_length=100, description="审批人姓名")
    notes: str | None = Field(None, description="备注")
    is_critical: bool = Field(False, description="是否关键作业")
    is_critical_reason: str | None = Field(None, description="关键作业判定理由")


class SpecialOperationReportCreate(SpecialOperationReportBase):
    """创建特殊作业报备"""
    pass


class SpecialOperationReportUpdate(BaseModel):
    """更新特殊作业报备"""

    report_no: str | None = Field(None, max_length=64, description="报备编号")
    permit_id: uuid.UUID | None = Field(None, description="关联作业票ID")
    operation_type: OperationType | None = Field(None, description="作业类型")
    operation_level: OperationLevel | None = Field(None, description="作业级别")
    department: str | None = Field(None, max_length=100, description="报备部门")
    location: str | None = Field(None, max_length=255, description="作业地点")
    equipment_tag: str | None = Field(None, max_length=100, description="设备位号")
    work_description: str | None = Field(None, description="作业内容描述")
    planned_start_time: datetime | None = Field(None, description="计划开始时间")
    planned_end_time: datetime | None = Field(None, description="计划结束时间")
    work_leader_name: str | None = Field(None, max_length=100, description="作业负责人姓名")
    operator_names: str | None = Field(None, description="作业人员姓名")
    guardian_name: str | None = Field(None, max_length=100, description="监护人姓名")
    risk_level: str | None = Field(None, max_length=20, description="风险等级")
    safety_measures: str | None = Field(None, description="安全措施")
    emergency_equipment: str | None = Field(None, description="应急消防器材")
    gas_analysis: str | None = Field(None, description="气体分析结果")
    risk_assessment: str | None = Field(None, description="风险评估描述")
    applicant_name: str | None = Field(None, max_length=100, description="报备申请人姓名")
    approver_name: str | None = Field(None, max_length=100, description="审批人姓名")
    status: ReportStatus | None = Field(None, description="状态")
    notes: str | None = Field(None, description="备注")
    is_critical: bool | None = Field(None, description="是否关键作业")
    is_critical_reason: str | None = Field(None, description="关键作业判定理由")


class SpecialOperationReportResponse(SpecialOperationReportBase):
    """特殊作业报备响应"""

    id: uuid.UUID
    approved_at: datetime | None = None
    rejection_reason: str | None = None
    status: str
    is_critical: bool = False
    is_critical_reason: str | None = None
    is_critical_updated_by: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SpecialOperationLedgerStats(BaseModel):
    """特殊作业台账统计"""
    operation_type: str = Field(..., description="作业类型")
    count: int = Field(..., description="总数")
    critical_count: int = Field(0, description="关键作业数")


class SetCriticalRequest(BaseModel):
    """手动设置关键作业标记"""
    is_critical: bool = Field(..., description="是否关键作业")
    reason: str | None = Field(None, description="修改理由")


class LedgerExportRequest(BaseModel):
    """台账导出请求 — AI自然语言筛选"""
    natural_query: str | None = Field(None, description="自然语言筛选条件，例如「导出上月所有特级动火作业」")
    operation_type: str | None = Field(None, description="作业类型")
    operation_level: str | None = Field(None, description="作业级别")
    risk_level: str | None = Field(None, description="风险等级")
    department: str | None = Field(None, description="部门")
    date_from: str | None = Field(None, description="开始日期 YYYY-MM-DD")
    date_to: str | None = Field(None, description="结束日期 YYYY-MM-DD")
    keyword: str | None = Field(None, description="关键词搜索")
    is_critical: bool | None = Field(None, description="是否关键作业")


class LedgerExportParsedFilters(BaseModel):
    """AI 解析后的台账筛选条件"""
    operation_type: str | None = None
    operation_level: str | None = None
    risk_level: str | None = None
    department: str | None = None
    date_from: str | None = None
    date_to: str | None = None
    keyword: str | None = None
    is_critical: bool | None = None
    explanation: str = Field("", description="AI 对筛选条件的解读说明")


# ── 危险源辨识台账导出 ──


class HazardLedgerExportRequest(BaseModel):
    """危险源辨识台账导出请求 — AI自然语言筛选"""
    natural_query: str | None = Field(None, description="自然语言筛选条件，例如「上月所有重大风险记录」")
    department: str | None = Field(None, description="部门")
    position: str | None = Field(None, description="岗位")
    risk_level: str | None = Field(None, description="风险等级: level_1/level_2/level_3/level_4")
    date_from: str | None = Field(None, description="创建时间起 YYYY-MM-DD")
    date_to: str | None = Field(None, description="创建时间止 YYYY-MM-DD")
    keyword: str | None = Field(None, description="关键词搜索（编号/部门/岗位/作业活动）")


class HazardLedgerExportParsedFilters(BaseModel):
    """AI 解析后的危险源辨识台账筛选条件"""
    department: str | None = None
    position: str | None = None
    risk_level: str | None = None
    date_from: str | None = None
    date_to: str | None = None
    keyword: str | None = None
    explanation: str = Field("", description="AI 对筛选条件的解读说明")


# ── 危险源风险选项（常规作业报备用） ──


class HazardRiskOption(BaseModel):
    """危险源风险选项 — 供常规作业报备选择关联危险源"""

    id: uuid.UUID
    hazard_id_no: str
    department: str
    position: str
    production_step: str
    specific_activity: str | None = None
    inherent_risk_level: str | None = None
    inherent_risk_label: str | None = None
    hazard_type: str | None = None
    possible_accident: str | None = None
    existing_engineering_controls: str | None = None
    existing_management_controls: str | None = None
    existing_ppe: str | None = None
    existing_emergency_measures: str | None = None

    class Config:
        from_attributes = True


# ── 每日风险作业报备 ──


class DailyRiskReportBase(BaseModel):
    """每日风险作业报备基础模式"""

    report_no: str = Field(..., max_length=64, description="报备编号")
    report_date: datetime = Field(..., description="报备作业日期")
    report_type: str = Field("regular", max_length=20, description="报备类型: regular(常规作业) / non_regular(非常规作业)")
    department: str | None = Field(None, max_length=100, description="报备部门")
    hazard_identification_id: uuid.UUID | None = Field(None, description="关联危险源辨识ID")
    operation_description: str = Field(..., description="风险作业描述")
    operation_steps: str | None = Field(None, description="作业步骤")
    hazard_factors: str | None = Field(None, description="危险因素")
    risk_level: str | None = Field(None, max_length=20, description="风险等级")
    control_measures: str | None = Field(None, description="控制措施")
    responsible_person: str | None = Field(None, max_length=100, description="作业负责人")
    operator_count: int | None = Field(None, description="作业人数")
    location: str | None = Field(None, max_length=255, description="作业地点")
    planned_start_time: datetime | None = Field(None, description="计划开始时间")
    planned_end_time: datetime | None = Field(None, description="计划结束时间")
    applicant_name: str | None = Field(None, max_length=100, description="报备申请人姓名")
    approver_name: str | None = Field(None, max_length=100, description="审批人姓名")
    notes: str | None = Field(None, description="备注")


class DailyRiskReportCreate(DailyRiskReportBase):
    """创建每日风险作业报备"""
    pass


class DailyRiskReportUpdate(BaseModel):
    """更新每日风险作业报备"""

    report_no: str | None = Field(None, max_length=64, description="报备编号")
    report_date: datetime | None = Field(None, description="报备作业日期")
    report_type: str | None = Field(None, max_length=20, description="报备类型（创建后不可修改）")
    department: str | None = Field(None, max_length=100, description="报备部门")
    hazard_identification_id: uuid.UUID | None = Field(None, description="关联危险源辨识ID")
    operation_description: str | None = Field(None, description="风险作业描述")
    operation_steps: str | None = Field(None, description="作业步骤")
    hazard_factors: str | None = Field(None, description="危险因素")
    risk_level: str | None = Field(None, max_length=20, description="风险等级")
    control_measures: str | None = Field(None, description="控制措施")
    responsible_person: str | None = Field(None, max_length=100, description="作业负责人")
    operator_count: int | None = Field(None, description="作业人数")
    location: str | None = Field(None, max_length=255, description="作业地点")
    planned_start_time: datetime | None = Field(None, description="计划开始时间")
    planned_end_time: datetime | None = Field(None, description="计划结束时间")
    applicant_name: str | None = Field(None, max_length=100, description="报备申请人姓名")
    approver_name: str | None = Field(None, max_length=100, description="审批人姓名")
    status: ReportStatus | None = Field(None, description="状态")
    notes: str | None = Field(None, description="备注")


class DailyRiskReportResponse(DailyRiskReportBase):
    """每日风险作业报备响应"""

    id: uuid.UUID
    approved_at: datetime | None = None
    rejection_reason: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== EHS变更管理 (MOC) Schemas ====================


# ── JSON 子记录 Schema ──


class RiskAssessmentItem(BaseModel):
    """风险评估记录"""

    method: str | None = Field(None, description="评估方法（LEC/LS/JHA/HAZOP等）")
    severity: str | None = Field(None, description="严重性")
    likelihood: str | None = Field(None, description="可能性")
    risk_level: str | None = Field(None, description="风险等级")
    description: str | None = Field(None, description="风险描述")
    control_measures: str | None = Field(None, description="控制措施")
    assessed_by: str | None = Field(None, max_length=100, description="评估人")
    assessed_date: str | None = Field(None, description="评估日期")
    participants: str | None = Field(None, description="参与人员")


class ApprovalChainItem(BaseModel):
    """审批链记录"""

    level: int = Field(..., description="审批层级")
    approver_role: str = Field(..., max_length=100, description="审批角色")
    approver: str | None = Field(None, max_length=100, description="审批人")
    decision: str = Field("pending", description="审批决定: pending/approved/rejected")
    comments: str | None = Field(None, description="审批意见")
    decided_at: str | None = Field(None, description="审批时间")


class ActionItem(BaseModel):
    """行动项"""

    task: str = Field(..., description="任务描述")
    owner: str | None = Field(None, max_length=100, description="责任人")
    due_date: str | None = Field(None, description="截止日期")
    status: str = Field("pending", description="状态: pending/in_progress/completed")
    completed_at: str | None = Field(None, description="完成时间")


class PSSRChecklistItem(BaseModel):
    """PSSR检查项"""

    item: str = Field(..., description="检查项")
    result: str = Field("na", description="结果: pass/fail/na")
    checked_by: str | None = Field(None, max_length=100, description="检查人")
    checked_at: str | None = Field(None, description="检查时间")
    remarks: str | None = Field(None, description="备注")


class VerificationDataSchema(BaseModel):
    """变更验证数据"""

    expected_effect_achieved: bool | None = Field(None, description="预期效果是否达成")
    comments: str | None = Field(None, description="验证意见")
    psi_updated: bool | None = Field(None, description="工艺安全信息是否已更新")
    documents_updated: bool | None = Field(None, description="相关文件是否已更新")
    accepted_by: str | None = Field(None, max_length=100, description="验收人")
    accepted_date: str | None = Field(None, description="验收日期")


class ClosureDataSchema(BaseModel):
    """变更关闭数据"""

    closed_by: str | None = Field(None, max_length=100, description="关闭人")
    closed_date: str | None = Field(None, description="关闭日期")
    temp_expiry_date: str | None = Field(None, description="临时变更到期日期")
    restored_date: str | None = Field(None, description="恢复原状日期")


# ── 主 Schema ──


class EhsChangeBase(BaseModel):
    """EHS变更基础字段"""

    change_no: str = Field(..., max_length=64, description="变更编号")
    title: str = Field(..., max_length=255, description="变更标题")
    change_type: str = Field(..., description="变更类型")
    change_grade: str = Field("general", description="变更等级")
    change_duration: str = Field("permanent", description="变更期限")
    department: str | None = Field(None, max_length=100, description="申请部门")
    location_unit: str | None = Field(None, max_length=255, description="所在单元/装置")
    description: str | None = Field(None, description="变更描述（变更前/变更后对比）")
    technical_basis: str | None = Field(None, description="变更技术依据")
    expected_start: datetime | None = Field(None, description="预期开始日期")
    expected_completion: datetime | None = Field(None, description="预期完成日期")
    actual_start: datetime | None = Field(None, description="实际开始日期")
    actual_completion: datetime | None = Field(None, description="实际完成日期")
    expected_effect: str | None = Field(None, description="预期效果")
    applicant_name: str | None = Field(None, max_length=100, description="申请人姓名")
    equipment_tags: list[str] | None = Field(None, description="关联设备位号")
    documents_to_update: list | None = Field(None, description="需更新的文件清单")
    attachments: list | None = Field(None, description="附件列表")
    risk_assessments: list | None = Field(None, description="风险评估记录")
    approval_chain: list | None = Field(None, description="审批链")
    action_items: list | None = Field(None, description="行动项")
    pssr_checklist: list | None = Field(None, description="PSSR检查清单")
    verification: dict | None = Field(None, description="变更验证数据")
    closure: dict | None = Field(None, description="变更关闭数据")
    linked_safety_check_id: uuid.UUID | None = Field(None, description="关联安全检查ID")
    notes: str | None = Field(None, description="备注")


class EhsChangeCreate(EhsChangeBase):
    """创建EHS变更"""

    pass


class EhsChangeUpdate(BaseModel):
    """更新EHS变更（所有字段可选）"""

    change_no: str | None = Field(None, max_length=64, description="变更编号")
    title: str | None = Field(None, max_length=255, description="变更标题")
    change_type: str | None = Field(None, description="变更类型")
    change_grade: str | None = Field(None, description="变更等级")
    change_duration: str | None = Field(None, description="变更期限")
    department: str | None = Field(None, max_length=100, description="申请部门")
    location_unit: str | None = Field(None, max_length=255, description="所在单元/装置")
    description: str | None = Field(None, description="变更描述")
    technical_basis: str | None = Field(None, description="变更技术依据")
    expected_start: datetime | None = Field(None, description="预期开始日期")
    expected_completion: datetime | None = Field(None, description="预期完成日期")
    actual_start: datetime | None = Field(None, description="实际开始日期")
    actual_completion: datetime | None = Field(None, description="实际完成日期")
    expected_effect: str | None = Field(None, description="预期效果")
    applicant_name: str | None = Field(None, max_length=100, description="申请人姓名")
    equipment_tags: list[str] | None = Field(None, description="关联设备位号")
    documents_to_update: list | None = Field(None, description="需更新的文件清单")
    attachments: list | None = Field(None, description="附件列表")
    risk_assessments: list | None = Field(None, description="风险评估记录")
    approval_chain: list | None = Field(None, description="审批链")
    action_items: list | None = Field(None, description="行动项")
    pssr_checklist: list | None = Field(None, description="PSSR检查清单")
    verification: dict | None = Field(None, description="变更验证数据")
    closure: dict | None = Field(None, description="变更关闭数据")
    linked_safety_check_id: uuid.UUID | None = Field(None, description="关联安全检查ID")
    notes: str | None = Field(None, description="备注")


class EhsChangeResponse(EhsChangeBase):
    """EHS变更响应"""

    id: uuid.UUID
    applicant_id: uuid.UUID | None = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── 工作流请求 Schema ──


class ApproveEhsChangeRequest(BaseModel):
    """审批EHS变更请求"""

    decision: str = Field(..., description="审批决定: approved/rejected")
    comments: str | None = Field(None, description="审批意见")


class CloseEhsChangeRequest(BaseModel):
    """关闭EHS变更请求"""

    closed_by: str | None = Field(None, max_length=100, description="关闭人")
    temp_expiry_date: str | None = Field(None, description="临时变更到期日期")
    restored_date: str | None = Field(None, description="恢复原状日期")


class AddRiskAssessmentRequest(BaseModel):
    """添加风险评估请求"""

    method: str | None = Field(None, description="评估方法")
    severity: str | None = Field(None, description="严重性")
    likelihood: str | None = Field(None, description="可能性")
    risk_level: str | None = Field(None, description="风险等级")
    description: str | None = Field(None, description="风险描述")
    control_measures: str | None = Field(None, description="控制措施")
    assessed_by: str | None = Field(None, max_length=100, description="评估人")
    assessed_date: str | None = Field(None, description="评估日期")
    participants: str | None = Field(None, description="参与人员")


class UpdateActionItemRequest(BaseModel):
    """更新行动项请求"""

    index: int = Field(..., ge=0, description="行动项索引")
    status: str = Field(..., description="状态: pending/in_progress/completed")


class SubmitVerificationRequest(BaseModel):
    """提交验证数据请求"""

    expected_effect_achieved: bool | None = Field(None, description="预期效果是否达成")
    comments: str | None = Field(None, description="验证意见")
    psi_updated: bool | None = Field(None, description="工艺安全信息是否已更新")
    documents_updated: bool | None = Field(None, description="相关文件是否已更新")
    accepted_by: str | None = Field(None, max_length=100, description="验收人")


# ==================== JSON 子记录 Schema ====================


class DetectionResultItem(BaseModel):
    """检测结果记录"""

    factor_name: str = Field(..., description="危害因素名称")
    factor_category: str = Field(..., description="危害因素类别: dust/chemical/physical")
    detection_value: float = Field(..., description="检测值")
    unit: str | None = Field(None, description="单位（mg/m³, dB(A), °C 等）")
    oel_limit: float | None = Field(None, description="职业接触限值（OEL）")
    compliance_status: str | None = Field(None, description="合规状态: compliant/exceeding/marginal")
    sampling_method: str | None = Field(None, description="采样方法")
    standard_ref: str | None = Field(None, description="标准参考")


class ExamResultItem(BaseModel):
    """体检项目结果"""

    item_name: str = Field(..., description="检查项目名称")
    category: str | None = Field(None, description="项目类别")
    result: str | None = Field(None, description="检查结果")
    reference_range: str | None = Field(None, description="参考范围")
    is_abnormal: bool | None = Field(None, description="是否异常")
    remarks: str | None = Field(None, description="备注")


class AbnormalityRecordItem(BaseModel):
    """异常处置记录"""

    abnormality_desc: str = Field(..., description="异常描述")
    corrective_action: str | None = Field(None, description="纠正措施")
    responsible_person: str | None = Field(None, max_length=100, description="责任人")
    deadline: str | None = Field(None, description="截止日期")
    status: str = Field("open", description="状态: open/investigating/corrected/closed")
    completed_at: str | None = Field(None, description="完成时间")
    remarks: str | None = Field(None, description="备注")


# ==================== 职业危害因素监测 Schemas ====================


class OhHazardMonitorBase(BaseModel):
    """职业危害因素监测基础字段"""

    monitor_no: str = Field(..., max_length=64, description="监测编号")
    workplace: str = Field(..., max_length=255, description="监测场所/车间")
    location: str | None = Field(None, max_length=255, description="具体监测点位")
    equipment_info: str | None = Field(None, max_length=255, description="关联设备/岗位")
    detection_type: str = Field(..., description="检测类型")
    detection_date: datetime | None = Field(None, description="检测日期")
    detection_agency: str | None = Field(None, max_length=255, description="检测机构")
    inspector_name: str | None = Field(None, max_length=100, description="检测人员")
    verifier_name: str | None = Field(None, max_length=100, description="验证人员")
    detection_results: list | None = Field(None, description="检测结果数组")
    abnormality_records: list | None = Field(None, description="异常处置记录")
    attachments: list | None = Field(None, description="附件列表")
    notes: str | None = Field(None, description="备注")


class OhHazardMonitorCreate(OhHazardMonitorBase):
    """创建危害因素监测"""

    pass


class OhHazardMonitorUpdate(BaseModel):
    """更新危害因素监测（所有字段可选）"""

    monitor_no: str | None = Field(None, max_length=64, description="监测编号")
    workplace: str | None = Field(None, max_length=255, description="监测场所/车间")
    location: str | None = Field(None, max_length=255, description="具体监测点位")
    equipment_info: str | None = Field(None, max_length=255, description="关联设备/岗位")
    detection_type: str | None = Field(None, description="检测类型")
    detection_date: datetime | None = Field(None, description="检测日期")
    detection_agency: str | None = Field(None, max_length=255, description="检测机构")
    inspector_name: str | None = Field(None, max_length=100, description="检测人员")
    verifier_name: str | None = Field(None, max_length=100, description="验证人员")
    detection_results: list | None = Field(None, description="检测结果数组")
    abnormality_records: list | None = Field(None, description="异常处置记录")
    attachments: list | None = Field(None, description="附件列表")
    notes: str | None = Field(None, description="备注")


class OhHazardMonitorResponse(OhHazardMonitorBase):
    """危害因素监测响应"""

    id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── 工作流请求 Schema ──


class VerifyMonitorRequest(BaseModel):
    """验证监测请求"""

    verified_by: str | None = Field(None, max_length=100, description="验证人")
    comments: str | None = Field(None, description="验证意见")


# ==================== 职业健康体检 Schemas ====================


class OhHealthExamBase(BaseModel):
    """职业健康体检基础字段"""

    exam_no: str = Field(..., max_length=64, description="体检编号")
    employee_name: str = Field(..., max_length=100, description="员工姓名")
    employee_id: str | None = Field(None, max_length=64, description="工号")
    department: str | None = Field(None, max_length=100, description="部门")
    job_position: str | None = Field(None, max_length=100, description="岗位")
    exam_type: str = Field(..., description="体检类型")
    exam_agency: str | None = Field(None, max_length=255, description="体检机构")
    scheduled_date: datetime | None = Field(None, description="计划体检日期")
    exam_date: datetime | None = Field(None, description="实际体检日期")
    report_date: datetime | None = Field(None, description="报告日期")
    hazard_factors: list | None = Field(None, description="关联的危害因素列表")
    overall_conclusion: str | None = Field(None, description="综合体检结论")
    exam_items: list | None = Field(None, description="体检项目结果")
    abnormality_records: list | None = Field(None, description="异常处置记录")
    attachments: list | None = Field(None, description="附件列表")
    notes: str | None = Field(None, description="备注")


class OhHealthExamCreate(OhHealthExamBase):
    """创建职业健康体检"""

    pass


class OhHealthExamUpdate(BaseModel):
    """更新职业健康体检（所有字段可选）"""

    exam_no: str | None = Field(None, max_length=64, description="体检编号")
    employee_name: str | None = Field(None, max_length=100, description="员工姓名")
    employee_id: str | None = Field(None, max_length=64, description="工号")
    department: str | None = Field(None, max_length=100, description="部门")
    job_position: str | None = Field(None, max_length=100, description="岗位")
    exam_type: str | None = Field(None, description="体检类型")
    exam_agency: str | None = Field(None, max_length=255, description="体检机构")
    scheduled_date: datetime | None = Field(None, description="计划体检日期")
    exam_date: datetime | None = Field(None, description="实际体检日期")
    report_date: datetime | None = Field(None, description="报告日期")
    hazard_factors: list | None = Field(None, description="关联的危害因素列表")
    overall_conclusion: str | None = Field(None, description="综合体检结论")
    exam_items: list | None = Field(None, description="体检项目结果")
    abnormality_records: list | None = Field(None, description="异常处置记录")
    attachments: list | None = Field(None, description="附件列表")
    notes: str | None = Field(None, description="备注")


class OhHealthExamResponse(OhHealthExamBase):
    """职业健康体检响应"""

    id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── 工作流请求 Schema ──


class SetExamConclusionRequest(BaseModel):
    """设置体检结论请求"""

    conclusion: str = Field(..., description="体检结论")
    remarks: str | None = Field(None, description="备注")


# ==================== 承包商管理 Schemas ====================


class ContractorStatus(str, Enum):
    """承包商状态枚举"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    BLACKLISTED = "blacklisted"


CONTRACTOR_STATUS_OPTIONS = [
    {"value": ContractorStatus.ACTIVE, "label": "活跃", "color": "green"},
    {"value": ContractorStatus.INACTIVE, "label": "停用", "color": "default"},
    {"value": ContractorStatus.BLACKLISTED, "label": "黑名单", "color": "red"},
]


class QualificationTypeEnum(str, Enum):
    """承包资质类型枚举"""

    CONSTRUCTION = "construction"
    INSTALLATION = "installation"
    MAINTENANCE = "maintenance"
    CLEANING = "cleaning"
    SECURITY = "security"
    OTHER = "other"


QUALIFICATION_TYPE_OPTIONS = [
    {"value": QualificationTypeEnum.CONSTRUCTION, "label": "建筑施工"},
    {"value": QualificationTypeEnum.INSTALLATION, "label": "设备安装"},
    {"value": QualificationTypeEnum.MAINTENANCE, "label": "检维修"},
    {"value": QualificationTypeEnum.CLEANING, "label": "保洁"},
    {"value": QualificationTypeEnum.SECURITY, "label": "安保"},
    {"value": QualificationTypeEnum.OTHER, "label": "其他"},
]


class QualificationLevelEnum(str, Enum):
    """资质等级枚举"""

    GRADE_A = "grade_a"
    GRADE_B = "grade_b"
    GRADE_C = "grade_c"


QUALIFICATION_LEVEL_OPTIONS = [
    {"value": QualificationLevelEnum.GRADE_A, "label": "甲级/一级"},
    {"value": QualificationLevelEnum.GRADE_B, "label": "乙级/二级"},
    {"value": QualificationLevelEnum.GRADE_C, "label": "丙级/三级"},
]


class ContractorTrainingStatusEnum(str, Enum):
    """承包商培训状态枚举"""

    UNTRAINED = "untrained"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    EXPIRED = "expired"


CONTRACTOR_TRAINING_STATUS_OPTIONS = [
    {"value": ContractorTrainingStatusEnum.UNTRAINED, "label": "未培训", "color": "default"},
    {"value": ContractorTrainingStatusEnum.IN_PROGRESS, "label": "培训中", "color": "processing"},
    {"value": ContractorTrainingStatusEnum.PASSED, "label": "已通过", "color": "green"},
    {"value": ContractorTrainingStatusEnum.EXPIRED, "label": "已过期", "color": "red"},
]


class WorkRecordStatusEnum(str, Enum):
    """施工记录状态枚举"""

    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EVALUATED = "evaluated"


WORK_RECORD_STATUS_OPTIONS = [
    {"value": WorkRecordStatusEnum.IN_PROGRESS, "label": "施工中", "color": "processing"},
    {"value": WorkRecordStatusEnum.COMPLETED, "label": "已完成", "color": "green"},
    {"value": WorkRecordStatusEnum.EVALUATED, "label": "已评价", "color": "blue"},
]


# ── 承包商主表 ──


class ContractorBase(BaseModel):
    """承包商基础模式"""

    contractor_no: str = Field(..., max_length=64, description="承包商编号")
    company_name: str = Field(..., max_length=255, description="公司名称")
    legal_representative: str | None = Field(None, max_length=100, description="法定代表人")
    contact_person: str = Field(..., max_length=100, description="联系人")
    contact_phone: str | None = Field(None, max_length=20, description="联系电话")
    business_scope: str | None = Field(None, description="经营范围")
    qualification_type: QualificationTypeEnum = Field(QualificationTypeEnum.OTHER, description="资质类型")
    qualification_level: QualificationLevelEnum | None = Field(None, description="资质等级")
    qualification_cert_no: str | None = Field(None, max_length=100, description="资质证书编号")
    qualification_expiry: datetime | None = Field(None, description="资质有效期至")
    safety_license_no: str | None = Field(None, max_length=100, description="安全生产许可证编号")
    safety_license_expiry: datetime | None = Field(None, description="安全生产许可证有效期")
    insurance_info: str | None = Field(None, description="保险信息")
    insurance_expiry: datetime | None = Field(None, description="保险有效期至")
    safety_officer_name: str | None = Field(None, max_length=100, description="安全负责人")
    safety_officer_phone: str | None = Field(None, max_length=20, description="安全负责人电话")
    special_op_personnel: list | None = Field(None, description="特种作业人员列表")
    notes: str | None = Field(None, description="备注")


class ContractorCreate(ContractorBase):
    """创建承包商"""
    pass


class ContractorUpdate(BaseModel):
    """更新承包商"""

    contractor_no: str | None = Field(None, max_length=64, description="承包商编号")
    company_name: str | None = Field(None, max_length=255, description="公司名称")
    legal_representative: str | None = Field(None, max_length=100, description="法定代表人")
    contact_person: str | None = Field(None, max_length=100, description="联系人")
    contact_phone: str | None = Field(None, max_length=20, description="联系电话")
    business_scope: str | None = Field(None, description="经营范围")
    qualification_type: QualificationTypeEnum | None = Field(None, description="资质类型")
    qualification_level: QualificationLevelEnum | None = Field(None, description="资质等级")
    qualification_cert_no: str | None = Field(None, max_length=100, description="资质证书编号")
    qualification_expiry: datetime | None = Field(None, description="资质有效期至")
    safety_license_no: str | None = Field(None, max_length=100, description="安全生产许可证编号")
    safety_license_expiry: datetime | None = Field(None, description="安全生产许可证有效期")
    insurance_info: str | None = Field(None, description="保险信息")
    insurance_expiry: datetime | None = Field(None, description="保险有效期至")
    safety_officer_name: str | None = Field(None, max_length=100, description="安全负责人")
    safety_officer_phone: str | None = Field(None, max_length=20, description="安全负责人电话")
    special_op_personnel: list | None = Field(None, description="特种作业人员列表")
    training_status: ContractorTrainingStatusEnum | None = Field(None, description="培训状态")
    training_date: datetime | None = Field(None, description="最近培训日期")
    safety_performance_score: int | None = Field(None, ge=0, le=100, description="安全绩效评分")
    status: ContractorStatus | None = Field(None, description="状态")
    notes: str | None = Field(None, description="备注")


class ContractorResponse(ContractorBase):
    """承包商响应"""

    id: uuid.UUID
    training_status: str
    training_date: datetime | None = None
    safety_performance_score: int | None = None
    blacklisted: bool = False
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── 施工记录子表 ──


class ContractorWorkRecordBase(BaseModel):
    """施工记录基础模式"""

    work_content: str = Field(..., description="施工内容")
    work_location: str | None = Field(None, max_length=255, description="施工地点")
    planned_start: datetime = Field(..., description="计划开始时间")
    planned_end: datetime = Field(..., description="计划结束时间")
    actual_start: datetime | None = Field(None, description="实际开始时间")
    actual_end: datetime | None = Field(None, description="实际结束时间")
    permit_id: uuid.UUID | None = Field(None, description="关联特殊作业票ID")
    leading_person: str | None = Field(None, max_length=100, description="带班负责人")
    worker_count: int | None = Field(None, ge=0, description="施工人数")
    safety_briefing_done: bool = Field(False, description="安全交底确认")
    violations: list | None = Field(None, description="违章记录")
    evaluation: dict | None = Field(None, description="评价")
    notes: str | None = Field(None, description="备注")


class ContractorWorkRecordCreate(ContractorWorkRecordBase):
    """创建施工记录"""
    pass


class ContractorWorkRecordUpdate(BaseModel):
    """更新施工记录"""

    work_content: str | None = Field(None, description="施工内容")
    work_location: str | None = Field(None, max_length=255, description="施工地点")
    actual_start: datetime | None = Field(None, description="实际开始时间")
    actual_end: datetime | None = Field(None, description="实际结束时间")
    leading_person: str | None = Field(None, max_length=100, description="带班负责人")
    worker_count: int | None = Field(None, ge=0, description="施工人数")
    safety_briefing_done: bool | None = Field(None, description="安全交底确认")
    violations: list | None = Field(None, description="违章记录")
    status: WorkRecordStatusEnum | None = Field(None, description="状态")
    notes: str | None = Field(None, description="备注")


class ContractorWorkRecordResponse(ContractorWorkRecordBase):
    """施工记录响应"""

    id: uuid.UUID
    contractor_id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EvaluateWorkRecordRequest(BaseModel):
    """评价施工记录请求"""

    score: int = Field(..., ge=0, le=100, description="评分")
    comments: str | None = Field(None, description="评价意见")
    evaluator: str | None = Field(None, max_length=100, description="评价人")
