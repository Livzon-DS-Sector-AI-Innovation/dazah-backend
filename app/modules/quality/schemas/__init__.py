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
from app.modules.quality.schemas.shared import PageParams
from app.modules.quality.schemas.deviations import (
    AiAnalysis,
    CreateDeviationRequest,
    CrossDeptReviewer,
    DeviationDetail,
    DeviationListItem,
    InvestigationRecord,
    ReviewOpinion,
    SubmitInvestigationRequest,
    SubmitReviewRequest,
    UpdateDeviationRequest,
)
from app.modules.quality.schemas.capa import (
    CapaApprovalRequest,
    CapaDetail,
    CapaItem,
    CapaListItem,
    CreateCapaRequest,
    DeptHeadConfirmation,
    ExecutionTrack,
    UpdateCapaRequest,
)
from app.modules.quality.schemas.contacts import (
    ConfirmProductionStatusRequest,
    CreateDepartmentContactRequest,
    DepartmentContactOut,
    DepartmentWeeklyConfirmationOut,
    UpdateDepartmentContactRequest,
)
from app.modules.quality.schemas.attachment_review import (
    AttachmentReviewOut,
    CreateAttachmentReviewRequest,
)
from app.modules.quality.schemas.statistics import (
    CapaStatistics,
    DeviationStatistics,
    StepBreakdownItem,
)

__all__ = [
    # CPV Product
    "ProductStatus",
    "CpvProductCreate",
    "CpvProductUpdate",
    "CpvProductResponse",
    "CpvProductListResponse",
    # CPV Parameter
    "ParameterType",
    "CpvParameterCreate",
    "CpvParameterUpdate",
    "CpvParameterResponse",
    # CPV Batch
    "DataType",
    "CpvBatchResponse",
    "CpvBatchWideResponse",
    # CPV Import
    "ImportMode",
    "ImportStatus",
    "CpvImportPreviewRequest",
    "CpvImportPreviewResponse",
    "CpvImportConfirmRequest",
    "CpvImportTaskResponse",
    # CPV Statistics
    "CpvStatisticsRequest",
    "CpvStatisticsResponse",
    "CpvTrendItem",
    "CpvTrendResponse",
    # Shared
    "PageParams",
    # Deviations
    "AiAnalysis",
    "InvestigationRecord",
    "ReviewOpinion",
    "CrossDeptReviewer",
    "DeviationListItem",
    "DeviationDetail",
    "CreateDeviationRequest",
    "UpdateDeviationRequest",
    "SubmitReviewRequest",
    "SubmitInvestigationRequest",
    # CAPA
    "CapaItem",
    "ExecutionTrack",
    "DeptHeadConfirmation",
    "CapaListItem",
    "CapaDetail",
    "CreateCapaRequest",
    "UpdateCapaRequest",
    "CapaApprovalRequest",
    # Department Contacts
    "DepartmentContactOut",
    "CreateDepartmentContactRequest",
    "UpdateDepartmentContactRequest",
    "DepartmentWeeklyConfirmationOut",
    "ConfirmProductionStatusRequest",
    # Attachment Review
    "AttachmentReviewOut",
    "CreateAttachmentReviewRequest",
    # Statistics
    "StepBreakdownItem",
    "DeviationStatistics",
    "CapaStatistics",
]
