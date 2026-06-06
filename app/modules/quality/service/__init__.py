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

__all__ = [
    # Product
    "create_product",
    "get_product_by_id",
    "get_products",
    "update_product",
    "delete_product",
    # Parameter
    "create_parameter",
    "get_parameter_by_id",
    "get_parameters",
    "update_parameter",
    "delete_parameter",
    # Batch
    "get_batches",
    "get_batches_wide",
    # Statistics
    "get_statistics",
    "get_trend_data",
    # Import
    "preview_import",
    "confirm_import",
    "get_import_tasks",
    "get_import_task_by_id",
]
