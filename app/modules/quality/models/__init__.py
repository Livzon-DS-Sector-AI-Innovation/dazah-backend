"""Quality module ORM models."""

from app.modules.quality.models.attachment_review import AttachmentReview
from app.modules.quality.models.capa import CAPA
from app.modules.quality.models.contacts import (
    DepartmentContact,
    DepartmentWeeklyConfirmation,
)
from app.modules.quality.models.cpv_batch import CpvBatch
from app.modules.quality.models.cpv_import_task import CpvImportTask
from app.modules.quality.models.cpv_parameter import CpvParameter
from app.modules.quality.models.cpv_product import CpvProduct
from app.modules.quality.models.cpv_value import CpvValue
from app.modules.quality.models.deviations import Deviation

__all__ = [
    "CpvProduct",
    "CpvParameter",
    "CpvBatch",
    "CpvValue",
    "CpvImportTask",
    "Deviation",
    "CAPA",
    "DepartmentContact",
    "DepartmentWeeklyConfirmation",
    "AttachmentReview",
]
