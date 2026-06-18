"""Production ORM models live here."""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base_model import BaseModel


class BatchStatus(str, PyEnum):
    """批次状态枚举"""

    DRAFT = "draft"  # 草稿
    RELEASED = "released"  # 已下达
    IN_PROGRESS = "in_progress"  # 执行中
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消


class PlanStatus(str, PyEnum):
    """计划状态枚举"""

    DRAFT = "draft"  # 草稿
    APPROVED = "approved"  # 已批准
    EXECUTING = "executing"  # 执行中
    COMPLETED = "completed"  # 已完成


class ProcessSpecStatus(str, PyEnum):
    """工艺规程状态枚举"""

    DRAFT = "draft"  # 草稿
    APPROVED = "approved"  # 已批准
    EFFECTIVE = "effective"  # 已生效
    ARCHIVED = "archived"  # 已归档


class TaskStatus(str, PyEnum):
    """任务状态枚举"""

    PENDING = "pending"  # 待执行
    ASSIGNED = "assigned"  # 已分配
    IN_PROGRESS = "in_progress"  # 执行中
    COMPLETED = "completed"  # 已完成


class OperationType(str, PyEnum):
    """操作类型枚举"""

    MATERIAL_ADD = "material_add"  # 投料
    TRANSFER = "transfer"  # 转序
    SAMPLING = "sampling"  # 取样
    EQUIPMENT_CHECK = "equipment_check"  # 设备检查
    PARAMETER_RECORD = "parameter_record"  # 参数记录
    PACKAGING = "packaging"  # 包装


class Batch(BaseModel):
    """批次主表"""

    __tablename__ = "batches"
    __table_args__ = (
        UniqueConstraint("batch_no", name="uq_batches_batch_no"),
        {"schema": "production"},
    )

    batch_no: Mapped[str] = mapped_column(String(64), nullable=False, comment="批次号")
    product_code: Mapped[str] = mapped_column(String(64), nullable=False, comment="产品编码")
    product_name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="产品名称")
    specification: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="规格")
    unit: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="单位")
    status: Mapped[str] = mapped_column(
        String(32),
        default="draft",
        server_default="draft",
        nullable=False,
        comment="状态",
    )
    planned_qty: Mapped[float | None] = mapped_column(Float, nullable=True, comment="计划数量")
    actual_qty: Mapped[float | None] = mapped_column(Float, nullable=True, comment="实际产出数量")
    input_qty: Mapped[float | None] = mapped_column(Float, nullable=True, comment="实际投入数量")
    process_spec_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("production.process_specs.id"), nullable=True, comment="工艺规程ID"
    )
    production_line: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="生产线")
    start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="开始时间")
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="结束时间")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")

    # 关系
    materials: Mapped[list["BatchMaterial"]] = relationship(
        "BatchMaterial", back_populates="batch", lazy="selectin"
    )
    records: Mapped[list["ProductionRecord"]] = relationship(
        "ProductionRecord", back_populates="batch", lazy="selectin"
    )
    material_balance: Mapped["MaterialBalance | None"] = relationship(
        "MaterialBalance", back_populates="batch", uselist=False, lazy="selectin"
    )


class BatchMaterial(BaseModel):
    """批次物料表"""

    __tablename__ = "batch_materials"
    __table_args__ = {"schema": "production"}

    batch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("production.batches.id"), nullable=False, comment="批次ID"
    )
    material_code: Mapped[str] = mapped_column(String(64), nullable=False, comment="物料编码")
    material_name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="物料名称")
    material_type: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="物料类型")
    unit: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="单位")
    planned_qty: Mapped[float | None] = mapped_column(Float, nullable=True, comment="计划用量")
    actual_qty: Mapped[float | None] = mapped_column(Float, nullable=True, comment="实际用量")
    lot_no: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="批号/批次")
    stage: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="工序阶段")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")

    # 关系
    batch: Mapped["Batch"] = relationship("Batch", back_populates="materials")


class ProductionPlan(BaseModel):
    """生产计划表"""

    __tablename__ = "production_plans"
    __table_args__ = (
        UniqueConstraint("plan_no", name="uq_production_plans_plan_no"),
        {"schema": "production"},
    )

    plan_no: Mapped[str] = mapped_column(String(64), nullable=False, comment="计划编号")
    plan_name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="计划名称")
    plan_type: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="计划类型:月计划/周计划")
    plan_month: Mapped[str | None] = mapped_column(String(7), nullable=True, comment="计划月份YYYY-MM")
    status: Mapped[str] = mapped_column(
        String(32),
        default="draft",
        server_default="draft",
        nullable=False,
        comment="状态",
    )
    total_batches: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="总批次")
    completed_batches: Mapped[int | None] = mapped_column(Integer, nullable=True, default=0, comment="已完成批次")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")

    # 关系
    tasks: Mapped[list["PlanTask"]] = relationship("PlanTask", back_populates="plan", lazy="selectin")


class PlanTask(BaseModel):
    """计划任务表"""

    __tablename__ = "plan_tasks"
    __table_args__ = {"schema": "production"}

    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("production.production_plans.id"), nullable=False, comment="计划ID"
    )
    product_code: Mapped[str] = mapped_column(String(64), nullable=False, comment="产品编码")
    product_name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="产品名称")
    batch_qty: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="批次数量")
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("identity.users.id"), nullable=True, comment="负责人"
    )
    assigned_to_name: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="负责人姓名")
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="计划完成日期")
    status: Mapped[str] = mapped_column(
        String(32),
        default="pending",
        server_default="pending",
        nullable=False,
        comment="状态",
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")

    # 关系
    plan: Mapped["ProductionPlan"] = relationship("ProductionPlan", back_populates="tasks")


class ProcessSpec(BaseModel):
    """工艺规程主表"""

    __tablename__ = "process_specs"
    __table_args__ = (
        UniqueConstraint("spec_code", "version", name="uq_process_specs_code_version"),
        {"schema": "production"},
    )

    spec_code: Mapped[str] = mapped_column(String(64), nullable=False, comment="规程编号")
    spec_name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="规程名称")
    product_code: Mapped[str] = mapped_column(String(64), nullable=False, comment="产品编码")
    product_name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="产品名称")
    version: Mapped[str] = mapped_column(String(20), nullable=False, server_default="1.0", comment="版本号")
    status: Mapped[str] = mapped_column(
        String(32),
        default="draft",
        server_default="draft",
        nullable=False,
        comment="状态",
    )
    effective_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="生效日期")
    approved_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("identity.users.id"), nullable=True, comment="批准人"
    )
    approved_by_name: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="批准人姓名")
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="批准时间")
    supersedes_version: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="替代版本")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")

    # 关系
    steps: Mapped[list["ProcessStep"]] = relationship("ProcessStep", back_populates="spec", lazy="selectin")


class ProcessStep(BaseModel):
    """工艺步骤表"""

    __tablename__ = "process_steps"
    __table_args__ = {"schema": "production"}

    spec_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("production.process_specs.id"), nullable=False, comment="规程ID"
    )
    step_no: Mapped[int] = mapped_column(Integer, nullable=False, comment="步骤序号")
    step_name: Mapped[str] = mapped_column(String(255), nullable=False, comment="步骤名称")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="步骤描述")
    equipment_type: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="设备类型")
    equipment_spec: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="设备规格")
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="持续时间(分钟)")
    sequence_order: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="排序顺序")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")

    # 关系
    spec: Mapped["ProcessSpec"] = relationship("ProcessSpec", back_populates="steps")
    parameters: Mapped[list["ProcessParameter"]] = relationship(
        "ProcessParameter", back_populates="step", lazy="selectin"
    )


class ProcessParameter(BaseModel):
    """工艺参数表"""

    __tablename__ = "process_parameters"
    __table_args__ = {"schema": "production"}

    step_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("production.process_steps.id"), nullable=False, comment="步骤ID"
    )
    param_name: Mapped[str] = mapped_column(String(255), nullable=False, comment="参数名称")
    param_code: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="参数编码")
    unit: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="单位")
    min_value: Mapped[float | None] = mapped_column(Float, nullable=True, comment="最小值")
    max_value: Mapped[float | None] = mapped_column(Float, nullable=True, comment="最大值")
    target_value: Mapped[float | None] = mapped_column(Float, nullable=True, comment="目标值")
    is_critical: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否关键参数")
    data_type: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="数据类型:numeric/text/boolean")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")

    # 关系
    step: Mapped["ProcessStep"] = relationship("ProcessStep", back_populates="parameters")


class ProductionRecord(BaseModel):
    """生产记录表"""

    __tablename__ = "production_records"
    __table_args__ = (
        UniqueConstraint("batch_id", "record_no", name="uq_production_records_batch_record"),
        {"schema": "production"},
    )

    batch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("production.batches.id"), nullable=False, comment="批次ID"
    )
    record_no: Mapped[str] = mapped_column(String(64), nullable=False, comment="记录编号")
    step_no: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="步骤序号")
    step_name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="步骤名称")
    operator: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("identity.users.id"), nullable=True, comment="操作人"
    )
    operator_name: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="操作人姓名")
    operation_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, comment="操作时间"
    )
    operation_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="操作类型",
    )
    parameters: Mapped[dict | None] = mapped_column(Text, nullable=True, comment="参数JSON")
    result: Mapped[str | None] = mapped_column(Text, nullable=True, comment="操作结果")
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")

    # 关系
    batch: Mapped["Batch"] = relationship("Batch", back_populates="records")


class MaterialBalance(BaseModel):
    """物料平衡表"""

    __tablename__ = "material_balances"
    __table_args__ = {"schema": "production"}

    batch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("production.batches.id"), nullable=False, unique=True, comment="批次ID"
    )
    input_qty: Mapped[float | None] = mapped_column(Float, nullable=True, comment="投入总量")
    output_qty: Mapped[float | None] = mapped_column(Float, nullable=True, comment="产出总量")
    loss_qty: Mapped[float | None] = mapped_column(Float, nullable=True, comment="损耗总量")
    balance_rate: Mapped[float | None] = mapped_column(Float, nullable=True, comment="平衡率(%)")
    min_balance_rate: Mapped[float] = mapped_column(Float, default=95.0, comment="最低平衡率(%)")
    is_balanced: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否平衡")
    deviation_rate: Mapped[float | None] = mapped_column(Float, nullable=True, comment="偏差率(%)")
    calculated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="计算时间")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")

    # 关系
    batch: Mapped["Batch"] = relationship("Batch", back_populates="material_balance")