from app.modules.quality.api import router as quality_router
from app.modules.quality.sampling_api import router as sampling_router
from app.modules.quality.iqc_api import router as iqc_router
from app.modules.quality.ipqc_api import router as ipqc_router
from app.modules.quality.fqc_api import router as fqc_router
from app.modules.quality.stability_api import router as stability_router
from app.modules.quality.deviation_api import router as deviation_router
from app.modules.quality.reagent_api import router as quality_reagent_router
from app.modules.quality.doc_check.api import router as doc_check_router
from app.modules.quality.static_data.api import router as static_data_router
from app.modules.quality.reagent_reminder_api import router as reagent_reminder_router

__all__ = [
    "quality_router",
    "sampling_router",
    "iqc_router",
    "ipqc_router",
    "fqc_router",
    "stability_router",
    "deviation_router",
    "quality_reagent_router",
    "doc_check_router",
    "static_data_router",
    "reagent_reminder_router",
]
