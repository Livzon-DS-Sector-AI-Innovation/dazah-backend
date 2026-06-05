"""Registration API routes."""

from app.modules.registration.api.drugs import router as drugs_router
from app.modules.registration.api.holidays import router as holidays_router
from app.shared.module_api import create_module_router
from app.shared.module_registry import MODULES_BY_CODE

router = create_module_router(MODULES_BY_CODE["registration"])

# 注册子路由
router.include_router(drugs_router, prefix="/drugs", tags=["申报进度-药品"])
router.include_router(holidays_router, prefix="/holidays", tags=["申报进度-节假日"])
