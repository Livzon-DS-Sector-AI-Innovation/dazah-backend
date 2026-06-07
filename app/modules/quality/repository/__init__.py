"""Quality module repository layer: re-export all public functions."""

from app.modules.quality.repository.cpv_product import (
    create_product,
    delete_product,
    get_product_by_id,
    get_products,
    update_product,
)
from app.modules.quality.repository.cpv_parameter import (
    create_parameter,
    delete_parameter,
    get_parameter_by_id,
    get_parameters,
    update_parameter,
)
from app.modules.quality.repository.cpv_batch import (
    get_batches,
    get_batches_wide,
)
from app.modules.quality.repository.cpv_value import (
    create_values,
    get_values_by_batch_id,
)
from app.modules.quality.repository.cpv_import_task import (
    create_import_task,
    get_import_task_by_id,
    get_import_tasks,
    update_import_task,
)
from app.modules.quality.repository.quality_management import (
    create_attachment_review,
    create_capa,
    create_department_contact,
    create_deviation,
    create_weekly_confirmation,
    delete_attachment_review,
    delete_capa,
    delete_department_contact,
    delete_deviation,
    delete_weekly_confirmation,
    exists_by_capa_code,
    exists_by_deviation_code,
    get_attachment_review_by_id,
    get_attachment_reviews,
    get_capa_by_id,
    get_capas,
    get_department_contact_by_department,
    get_department_contact_by_id,
    get_department_contacts,
    get_deviations,
    get_deviation_by_id,
    get_weekly_confirmation_by_department_week,
    get_weekly_confirmation_by_id,
    get_weekly_confirmations,
    update_attachment_review,
    update_capa,
    update_department_contact,
    update_deviation,
    update_weekly_confirmation,
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
    # CPV Value
    "create_values",
    "get_values_by_batch_id",
    # CPV Import Task
    "create_import_task",
    "get_import_task_by_id",
    "get_import_tasks",
    "update_import_task",
    # Deviations
    "exists_by_deviation_code",
    "create_deviation",
    "get_deviation_by_id",
    "get_deviations",
    "update_deviation",
    "delete_deviation",
    # CAPA
    "exists_by_capa_code",
    "create_capa",
    "get_capa_by_id",
    "get_capas",
    "update_capa",
    "delete_capa",
    # Department Contacts
    "get_department_contact_by_id",
    "get_department_contact_by_department",
    "get_department_contacts",
    "create_department_contact",
    "update_department_contact",
    "delete_department_contact",
    # Weekly Confirmations
    "get_weekly_confirmation_by_id",
    "get_weekly_confirmation_by_department_week",
    "get_weekly_confirmations",
    "create_weekly_confirmation",
    "update_weekly_confirmation",
    "delete_weekly_confirmation",
    # Attachment Reviews
    "get_attachment_review_by_id",
    "get_attachment_reviews",
    "create_attachment_review",
    "update_attachment_review",
    "delete_attachment_review",
]
