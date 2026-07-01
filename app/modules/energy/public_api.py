"""Energy module public API — cross-module access points.

Other modules should import from this file instead of directly accessing
internal service/repository/models.
"""

from app.modules.energy.service import EnergyService
from app.modules.energy.repository import EnergyRepository
from app.modules.energy.schemas import (
    EnergyDeviceConfigCreate,
    EnergyDeviceConfigResponse,
    EnergyAlertRuleCreate,
    EnergyAlertRuleResponse,
)

__all__ = [
    "EnergyService",
    "EnergyRepository",
    "EnergyDeviceConfigCreate",
    "EnergyDeviceConfigResponse",
    "EnergyAlertRuleCreate",
    "EnergyAlertRuleResponse",
]
