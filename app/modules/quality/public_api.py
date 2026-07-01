"""Quality module public API — cross-module access points.

Other modules should import from this file instead of directly accessing
internal service/repository/models.
"""

from app.modules.quality.service.quality_management import QualityManagementService
from app.modules.quality.repository.quality_management import QualityManagementRepository
from app.modules.quality.schemas.deviations import (
    DeviationCreate,
    DeviationUpdate,
    DeviationResponse,
)
from app.modules.quality.schemas.capa import (
    CAPACreate,
    CAPAUpdate,
    CAPAResponse,
)

__all__ = [
    "QualityManagementService",
    "QualityManagementRepository",
    "DeviationCreate",
    "DeviationUpdate",
    "DeviationResponse",
    "CAPACreate",
    "CAPAUpdate",
    "CAPAResponse",
]
