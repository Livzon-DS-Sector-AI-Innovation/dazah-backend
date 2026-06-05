"""Registration module schemas."""

from app.modules.registration.schemas.drug import (
    DrugCreate,
    DrugNodeCreate,
    DrugNodeResponse,
    DrugNodeUpdate,
    DrugResponse,
    DrugUpdate,
    DrugWithNodesResponse,
)
from app.modules.registration.schemas.holiday import (
    HolidayCreate,
    HolidayResponse,
)
from app.modules.registration.schemas.review import (
    NodeCalculation,
    ReviewNodeConfig,
    StatsResponse,
)

__all__ = [
    "DrugCreate",
    "DrugNodeCreate",
    "DrugNodeResponse",
    "DrugNodeUpdate",
    "DrugResponse",
    "DrugUpdate",
    "DrugWithNodesResponse",
    "HolidayCreate",
    "HolidayResponse",
    "NodeCalculation",
    "ReviewNodeConfig",
    "StatsResponse",
]
