"""Equipment module schemas."""

from app.modules.equipment.schemas.calibration import (
    CalibrationPlanCreate,
    CalibrationPlanResponse,
    CalibrationPlanStatus,
    CalibrationPlanUpdate,
    CalibrationRecordCreate,
    CalibrationRecordResponse,
    CalibrationResult,
    CalibrationType,
)
from app.modules.equipment.schemas.equipment import (
    EquipmentCategoryCreate,
    EquipmentCategoryResponse,
    EquipmentCategoryTree,
    EquipmentCategoryUpdate,
    EquipmentCreate,
    EquipmentResponse,
    EquipmentStatistics,
    EquipmentStatus,
    EquipmentUpdate,
    LocationCreate,
    LocationResponse,
    LocationTree,
    LocationUpdate,
)
from app.modules.equipment.schemas.failure_code import (
    FailureCodeCreate,
    FailureCodeResponse,
    FailureCodeType,
    FailureCodeUpdate,
)
from app.modules.equipment.schemas.work_order import (
    VerificationResult,
    WorkOrderAssign,
    WorkOrderComplete,
    WorkOrderCreate,
    WorkOrderPriority,
    WorkOrderResponse,
    WorkOrderStatistics,
    WorkOrderStatus,
    WorkOrderType,
    WorkOrderVerify,
)

__all__ = [
    # equipment
    "EquipmentStatus",
    "EquipmentCategoryCreate",
    "EquipmentCategoryUpdate",
    "EquipmentCategoryResponse",
    "EquipmentCategoryTree",
    "LocationCreate",
    "LocationUpdate",
    "LocationResponse",
    "LocationTree",
    "EquipmentCreate",
    "EquipmentUpdate",
    "EquipmentResponse",
    "EquipmentStatistics",
    # failure code
    "FailureCodeType",
    "FailureCodeCreate",
    "FailureCodeUpdate",
    "FailureCodeResponse",
    # work order
    "WorkOrderType",
    "WorkOrderPriority",
    "WorkOrderStatus",
    "VerificationResult",
    "WorkOrderCreate",
    "WorkOrderAssign",
    "WorkOrderComplete",
    "WorkOrderVerify",
    "WorkOrderResponse",
    "WorkOrderStatistics",
    # calibration
    "CalibrationType",
    "CalibrationResult",
    "CalibrationPlanStatus",
    "CalibrationPlanCreate",
    "CalibrationPlanUpdate",
    "CalibrationPlanResponse",
    "CalibrationRecordCreate",
    "CalibrationRecordResponse",
]
