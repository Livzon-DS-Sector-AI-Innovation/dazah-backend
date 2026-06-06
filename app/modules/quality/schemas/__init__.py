"""Quality module schemas."""

from app.modules.quality.schemas.cpv_product import (
    CpvProductCreate,
    CpvProductListResponse,
    CpvProductResponse,
    CpvProductUpdate,
    ProductStatus,
)
from app.modules.quality.schemas.cpv_parameter import (
    CpvParameterCreate,
    CpvParameterResponse,
    CpvParameterUpdate,
    ParameterType,
)
from app.modules.quality.schemas.cpv_batch import (
    CpvBatchResponse,
    CpvBatchWideResponse,
    DataType,
)
from app.modules.quality.schemas.cpv_import import (
    CpvImportConfirmRequest,
    CpvImportPreviewRequest,
    CpvImportPreviewResponse,
    CpvImportTaskResponse,
    ImportMode,
    ImportStatus,
)
from app.modules.quality.schemas.cpv_statistics import (
    CpvStatisticsRequest,
    CpvStatisticsResponse,
    CpvTrendItem,
    CpvTrendResponse,
)

__all__ = [
    # Product
    "ProductStatus",
    "CpvProductCreate",
    "CpvProductUpdate",
    "CpvProductResponse",
    "CpvProductListResponse",
    # Parameter
    "ParameterType",
    "CpvParameterCreate",
    "CpvParameterUpdate",
    "CpvParameterResponse",
    # Batch
    "DataType",
    "CpvBatchResponse",
    "CpvBatchWideResponse",
    # Import
    "ImportMode",
    "ImportStatus",
    "CpvImportPreviewRequest",
    "CpvImportPreviewResponse",
    "CpvImportConfirmRequest",
    "CpvImportTaskResponse",
    # Statistics
    "CpvStatisticsRequest",
    "CpvStatisticsResponse",
    "CpvTrendItem",
    "CpvTrendResponse",
]
