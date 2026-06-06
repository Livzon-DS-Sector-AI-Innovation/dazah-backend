"""Quality module ORM models."""

from app.modules.quality.models.cpv_product import CpvProduct
from app.modules.quality.models.cpv_parameter import CpvParameter
from app.modules.quality.models.cpv_batch import CpvBatch
from app.modules.quality.models.cpv_value import CpvValue
from app.modules.quality.models.cpv_import_task import CpvImportTask

__all__ = [
    "CpvProduct",
    "CpvParameter",
    "CpvBatch",
    "CpvValue",
    "CpvImportTask",
]
