"""Registration module schemas."""

from app.modules.registration.schemas.authorization import (
    AuthorizationLetterCreate,
    AuthorizationLetterListItem,
    AuthorizationLetterResponse,
    ProductInfo,
    SupplementaryReplyCreate,
    SupplementaryReplyListItem,
    SupplementaryReplyResponse,
)
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
    "AuthorizationLetterCreate",
    "AuthorizationLetterListItem",
    "AuthorizationLetterResponse",
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
    "ProductInfo",
    "ReviewNodeConfig",
    "StatsResponse",
    "SupplementaryReplyCreate",
    "SupplementaryReplyListItem",
    "SupplementaryReplyResponse",
]
