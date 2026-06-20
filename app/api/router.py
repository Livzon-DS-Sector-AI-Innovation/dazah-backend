from fastapi import APIRouter

from app.modules.administration import router as administration_router
from app.modules.dossier_writer import router as dossier_writer_router
from app.modules.energy import router as energy_router
from app.modules.environment import router as environment_router
from app.modules.equipment import router as equipment_router
from app.modules.hr import router as hr_router
from app.modules.procurement import router as procurement_router
from app.modules.production import router as production_router
from app.modules.quality import router as quality_router
from app.modules.registration import router as registration_router
from app.modules.research import router as research_router
from app.modules.regulatory_tracker import router as regulatory_tracker_router
from app.modules.production.label_verification_api import router as label_verification_router
from app.modules.safety import router as safety_router
from app.modules.warehouse import router as warehouse_router
from app.modules.ai_parser import router as ai_parser_router
from app.platform.identity.api import (
    dept_router,
    personnel_router,
    sync_router,
    user_router,
)
from app.platform.identity.api import (
    router as identity_router,
)
from app.platform.system import router as system_router

api_router = APIRouter()

api_router.include_router(identity_router, prefix="/identity", tags=["身份认证"])
api_router.include_router(user_router, prefix="/identity", tags=["用户信息"])
api_router.include_router(dept_router, prefix="/identity", tags=["组织架构"])
api_router.include_router(personnel_router, prefix="/identity", tags=["人员名单"])
api_router.include_router(sync_router, prefix="/identity", tags=["飞书同步"])
api_router.include_router(system_router, prefix="/system", tags=["系统"])
api_router.include_router(production_router, prefix="/production", tags=["生产管理"])
api_router.include_router(equipment_router, prefix="/equipment", tags=["设备管理"])
api_router.include_router(safety_router, prefix="/safety", tags=["安全管理"])
api_router.include_router(environment_router, prefix="/environment", tags=["环保管理"])
api_router.include_router(energy_router, prefix="/energy", tags=["能源管理"])
api_router.include_router(warehouse_router, prefix="/warehouse", tags=["仓储管理"])
api_router.include_router(procurement_router, prefix="/procurement", tags=["采购管理"])
api_router.include_router(
    administration_router,
    prefix="/administration",
    tags=["行政管理"],
)
api_router.include_router(hr_router, prefix="/hr", tags=["人事管理"])
api_router.include_router(research_router, prefix="/research", tags=["研发管理"])
api_router.include_router(
    registration_router,
    prefix="/registration",
    tags=["注册管理"],
)
api_router.include_router(quality_router, prefix="/quality", tags=["质量管理"])
api_router.include_router(label_verification_router, prefix="/quality", tags=["质量管理 - 标签复核"])
api_router.include_router(regulatory_tracker_router, tags=["法规追踪"])
api_router.include_router(
    dossier_writer_router,
    prefix="/dossier-writer",
    tags=["申报资料撰写"],
)
api_router.include_router(ai_parser_router, prefix="/ai", tags=["AI解析"])
