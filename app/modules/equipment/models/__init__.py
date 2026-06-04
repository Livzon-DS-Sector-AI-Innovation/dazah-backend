"""Equipment ORM models."""

from sqlalchemy import Boolean, Column, DateTime, PrimaryKeyConstraint, Table, text

from app.modules.equipment.models.calibration import (
    CalibrationPlan,
    CalibrationRecord,
)
from app.modules.equipment.models.equipment import (
    Equipment,
    EquipmentCategory,
    Location,
)
from app.modules.equipment.models.failure_code import (
    FailureAction,
    FailureCause,
    FailureSymptom,
)
from app.modules.equipment.models.work_order import WorkOrder
from app.shared.base_model import Base

# Stub tables for FK references from WorkOrder (full implementation in P3/P4)
Table(
    "maintenance_plans",
    Base.metadata,
    Column("id", primary_key=True),
    Column("created_at", DateTime(timezone=True), server_default=text("now()"), nullable=False),
    Column("updated_at", DateTime(timezone=True), server_default=text("now()"), nullable=False),
    Column("is_deleted", Boolean, server_default=text("false"), nullable=False),
    PrimaryKeyConstraint("id"),
    schema="equipment",
)

Table(
    "inspection_templates",
    Base.metadata,
    Column("id", primary_key=True),
    Column("created_at", DateTime(timezone=True), server_default=text("now()"), nullable=False),
    Column("updated_at", DateTime(timezone=True), server_default=text("now()"), nullable=False),
    Column("is_deleted", Boolean, server_default=text("false"), nullable=False),
    PrimaryKeyConstraint("id"),
    schema="equipment",
)

__all__ = [
    "CalibrationPlan",
    "CalibrationRecord",
    "Equipment",
    "EquipmentCategory",
    "FailureAction",
    "FailureCause",
    "FailureSymptom",
    "Location",
    "WorkOrder",
]
