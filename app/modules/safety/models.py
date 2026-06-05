"""Safety ORM models."""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base_model import BaseModel


# ==================== Enums ====================


class CheckType(str, PyEnum):
    """检查类型枚举"""

    DAILY = "daily"  # 日常检查
    SPECIAL = "special"  # 专项检查
    COMPREHENSIVE = "comprehensive"  # 综合检查
    HOLIDAY = "holiday"  # 节假日检查


class HazardType(str, PyEnum):
    """隐患类型枚举"""

    UNSAFE_CONDITION = "unsafe_condition"  # 物的不安全状态
    UNSAFE_ACTION = "unsafe_action"  # 人的不安全行为
    MANAGEMENT_DEFECT = "management_defect"  # 管理缺陷
    ENVIRONMENTAL = "environmental"  # 环境因素


class HazardLevel(str, PyEnum):
    """隐患等级枚举"""

    GENERAL = "general"  # 一般隐患
    MAJOR = "major"  # 重大隐患


class AccidentType(str, PyEnum):
    """事故类型枚举"""

    INJURY = "injury"  # 工伤事故
    FIRE = "fire"  # 火灾
    EXPLOSION = "explosion"  # 爆炸
    LEAKAGE = "leakage"  # 泄漏
    EQUIPMENT = "equipment"  # 设备事故
    OTHER = "other"  # 其他


class AccidentLevel(str, PyEnum):
    """事故等级枚举"""

    GENERAL = "general"  # 一般事故
    SERIOUS = "serious"  # 较大事故
    MAJOR = "major"  # 重大事故
    CATASTROPHIC = "catastrophic"  # 特别重大事故


class TrainingType(str, PyEnum):
    """培训类型枚举"""

    INDUCTION = "induction"  # 入职培训
    ANNUAL = "annual"  # 年度培训
    SPECIAL = "special"  # 专项培训
    EMERGENCY = "emergency"  # 应急培训


class TrainingMode(str, PyEnum):
    """培训方式枚举"""

    ONLINE = "online"  # 线上
    OFFLINE = "offline"  # 线下
    BLENDED = "blended"  # 混合


# ==================== 安全检查 ====================


class SafetyCheck(BaseModel):
    """安全检查表"""

    __tablename__ = "safety_checks"
    __table_args__ = (
        UniqueConstraint("check_no", name="uq_safety_checks_check_no"),
        {"schema": "safety"},
    )

    check_no: Mapped[str] = mapped_column(String(64), nullable=False, comment="检查编号")
    check_type: Mapped[str] = mapped_column(
        String(32), nullable=False, default="daily", server_default="daily", comment="检查类型"
    )
    check_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, comment="检查日期"
    )
    department: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="检查部门")
    inspector: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("identity.users.id"), nullable=True, comment="检查人"
    )
    inspector_name: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="检查人姓名")
    location: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="检查地点")
    findings: Mapped[str | None] = mapped_column(Text, nullable=True, comment="检查发现")
    result: Mapped[str | None] = mapped_column(
        String(32), nullable=True, comment="检查结果: qualified/unqualified/need_rectification"
    )
    rectification_required: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否需要整改")
    rectification_deadline: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="整改期限"
    )
    rectification_status: Mapped[str | None] = mapped_column(
        String(32), default="pending", nullable=True, comment="整改进度"
    )
    status: Mapped[str] = mapped_column(
        String(32), default="draft", server_default="draft", nullable=False, comment="状态"
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")

    # 关系
    hazards: Mapped[list["HazardReport"]] = relationship(
        "HazardReport", back_populates="safety_check", lazy="selectin"
    )


# ==================== 隐患排查 ====================


class HazardReport(BaseModel):
    """隐患报告表"""

    __tablename__ = "hazard_reports"
    __table_args__ = (
        UniqueConstraint("hazard_no", name="uq_hazard_reports_hazard_no"),
        {"schema": "safety"},
    )

    hazard_no: Mapped[str] = mapped_column(String(64), nullable=False, comment="隐患编号")
    hazard_type: Mapped[str] = mapped_column(String(32), nullable=False, comment="隐患类型")
    hazard_level: Mapped[str] = mapped_column(
        String(16), nullable=False, default="general", comment="隐患等级"
    )
    description: Mapped[str] = mapped_column(Text, nullable=False, comment="隐患描述")
    location: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="地点/部位")
    discovered_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("identity.users.id"), nullable=True, comment="发现人"
    )
    discovered_by_name: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="发现人姓名")
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=None, nullable=False, comment="发现时间"
    )
    department: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="责任部门")
    control_measures: Mapped[str | None] = mapped_column(Text, nullable=True, comment="管控措施")
    deadline: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="整改期限"
    )
    rectification_status: Mapped[str] = mapped_column(
        String(32), default="pending", server_default="pending", nullable=False, comment="整改进度"
    )
    verified_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("identity.users.id"), nullable=True, comment="验证人"
    )
    verified_by_name: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="验证人姓名")
    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="验证时间"
    )
    status: Mapped[str] = mapped_column(
        String(32), default="open", server_default="open", nullable=False, comment="状态"
    )
    check_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("safety.safety_checks.id"), nullable=True, comment="关联检查ID"
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")

    # 关系
    safety_check: Mapped["SafetyCheck | None"] = relationship(
        "SafetyCheck", back_populates="hazards"
    )


# ==================== 事故管理 ====================


class Accident(BaseModel):
    """事故登记表"""

    __tablename__ = "accidents"
    __table_args__ = (
        UniqueConstraint("accident_no", name="uq_accidents_accident_no"),
        {"schema": "safety"},
    )

    accident_no: Mapped[str] = mapped_column(String(64), nullable=False, comment="事故编号")
    accident_type: Mapped[str] = mapped_column(String(32), nullable=False, comment="事故类型")
    accident_level: Mapped[str] = mapped_column(
        String(32), nullable=False, default="general", comment="事故等级"
    )
    happened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, comment="发生时间"
    )
    location: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="发生地点")
    description: Mapped[str] = mapped_column(Text, nullable=False, comment="事故描述")
    casualties: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="伤亡情况")
    property_damage: Mapped[float | None] = mapped_column(Float, nullable=True, comment="财产损失(元)")
    direct_cause: Mapped[str | None] = mapped_column(Text, nullable=True, comment="直接原因")
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True, comment="根本原因")
    handling_measures: Mapped[str | None] = mapped_column(Text, nullable=True, comment="处理措施")
    corrective_actions: Mapped[str | None] = mapped_column(Text, nullable=True, comment="纠正预防措施")
    status: Mapped[str] = mapped_column(
        String(32), default="reported", server_default="reported", nullable=False, comment="状态"
    )
    reported_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("identity.users.id"), nullable=True, comment="报告人"
    )
    reported_by_name: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="报告人姓名")
    reported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, comment="报告时间"
    )
    investigator: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("identity.users.id"), nullable=True, comment="调查人"
    )
    investigator_name: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="调查人姓名")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")


# ==================== 安全培训 ====================


class SafetyTraining(BaseModel):
    """安全培训表"""

    __tablename__ = "safety_trainings"
    __table_args__ = (
        UniqueConstraint("training_no", name="uq_safety_trainings_training_no"),
        {"schema": "safety"},
    )

    training_no: Mapped[str] = mapped_column(String(64), nullable=False, comment="培训编号")
    training_name: Mapped[str] = mapped_column(String(255), nullable=False, comment="培训名称")
    training_type: Mapped[str] = mapped_column(
        String(32), nullable=False, default="annual", comment="培训类型"
    )
    training_mode: Mapped[str] = mapped_column(
        String(16), nullable=False, default="offline", comment="培训方式"
    )
    trainer: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("identity.users.id"), nullable=True, comment="培训讲师"
    )
    trainer_name: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="讲师姓名")
    training_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, comment="培训日期"
    )
    duration_hours: Mapped[float | None] = mapped_column(Float, nullable=True, comment="培训时长(小时)")
    location: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="培训地点")
    content: Mapped[str | None] = mapped_column(Text, nullable=True, comment="培训内容")
    department: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="培训部门")
    status: Mapped[str] = mapped_column(
        String(32), default="draft", server_default="draft", nullable=False, comment="状态"
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")

    # 关系
    records: Mapped[list["TrainingRecord"]] = relationship(
        "TrainingRecord", back_populates="training", lazy="selectin"
    )


class TrainingRecord(BaseModel):
    """培训记录（签到/考核）子表"""

    __tablename__ = "training_records"
    __table_args__ = {"schema": "safety"}

    training_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("safety.safety_trainings.id"),
        nullable=False,
        comment="培训ID",
    )
    employee_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("identity.users.id"), nullable=True, comment="员工ID"
    )
    employee_name: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="员工姓名")
    department: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="部门")
    attendance: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否出席")
    score: Mapped[float | None] = mapped_column(Float, nullable=True, comment="考核成绩")
    passed: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment="是否合格")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")

    # 关系
    training: Mapped["SafetyTraining"] = relationship("SafetyTraining", back_populates="records")
