"""Quality module service layer: re-export all public functions."""

from app.modules.quality.service.cpv_product import (
    create_product,
    delete_product,
    get_product_by_id,
    get_products,
    update_product,
)
from app.modules.quality.service.cpv_parameter import (
    create_parameter,
    delete_parameter,
    get_parameter_by_id,
    get_parameters,
    update_parameter,
)
from app.modules.quality.service.cpv_batch import (
    get_batches,
    get_batches_wide,
)
from app.modules.quality.service.cpv_statistics import (
    get_statistics,
    get_trend_data,
)
from app.modules.quality.service.cpv_import import (
    confirm_import,
    get_import_task_by_id,
    get_import_tasks,
    preview_import,
)
from app.modules.quality.service.quality_management import (
    get_deviation_list,
    get_deviation_detail,
    create_deviation,
    update_deviation,
    delete_deviation,
    submit_investigation,
    submit_review,
    submit_final_code,
    resubmit_deviation,
    get_capa_list,
    get_capa_detail,
    create_capa,
    update_capa,
    delete_capa,
    get_department_contact_list,
    upsert_department_contact,
    delete_department_contact,
    get_deviation_statistics,
    get_capa_statistics,
    list_attachment_reviews,
    create_attachment_review,
    delete_attachment_review,
)

__all__ = [
    # CPV Product
    "create_product",
    "get_product_by_id",
    "get_products",
    "update_product",
    "delete_product",
    # CPV Parameter
    "create_parameter",
    "get_parameter_by_id",
    "get_parameters",
    "update_parameter",
    "delete_parameter",
    # CPV Batch
    "get_batches",
    "get_batches_wide",
    # CPV Statistics
    "get_statistics",
    "get_trend_data",
    # CPV Import
    "preview_import",
    "confirm_import",
    "get_import_tasks",
    "get_import_task_by_id",
    # Deviations
    "get_deviation_list",
    "get_deviation_detail",
    "create_deviation",
    "update_deviation",
    "delete_deviation",
    "submit_investigation",
    "submit_review",
    "submit_final_code",
    "resubmit_deviation",
    "get_deviation_statistics",
    # CAPA
    "get_capa_list",
    "get_capa_detail",
    "create_capa",
    "update_capa",
    "delete_capa",
    "get_capa_statistics",
    # Department Contacts
    "get_department_contact_list",
    "upsert_department_contact",
    "delete_department_contact",
    # Attachment Reviews
    "list_attachment_reviews",
    "create_attachment_review",
    "delete_attachment_review",
]
