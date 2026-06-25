"""Quality API routes."""

from fastapi import APIRouter

from app.modules.quality.api.cpv_products import router as cpv_products_router
from app.modules.quality.api.cpv_import import router as cpv_import_router
from app.modules.quality.api.quality_management import router as quality_management_router

router = APIRouter()

# Mount CPV sub-routes
router.include_router(cpv_products_router, prefix="/cpv", tags=["CPV-产品"])
router.include_router(cpv_import_router, prefix="/cpv", tags=["CPV-导入"])

# Mount quality management routes (deviations, CAPA, contacts, etc.)
router.include_router(quality_management_router, tags=["Quality-Management"])
