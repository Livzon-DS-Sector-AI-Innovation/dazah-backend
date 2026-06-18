from fastapi import APIRouter

from app.modules.administration import router as administration_router
from app.modules.energy import router as energy_router
from app.modules.environment import router as environment_router
from app.modules.equipment import router as equipment_router
from app.modules.hr import router as hr_router
from app.modules.procurement import router as procurement_router
from app.modules.production import router as production_router
from app.modules.quality import quality_router
from app.modules.quality.sampling_api import router as sampling_router
from app.modules.quality.iqc_api import router as iqc_router
from app.modules.quality.ipqc_api import router as ipqc_router
from app.modules.quality.fqc_api import router as fqc_router
from app.modules.quality.stability_api import router as stability_router
from app.modules.quality.instrument_api import router as instrument_router
from app.modules.quality.deviation_api import router as deviation_router
from app.modules.quality.deviation_report_api import router as deviation_report_router
from app.modules.quality.deviation_report_api import router as deviation_report_router
from app.modules.quality.deviation_automation_api import router as deviation_automation_router
from app.modules.quality.reagent_api import router as quality_reagent_router
from app.modules.quality.material_report_api import router as material_report_router
from app.modules.quality.inspection_table_api import router as inspection_table_router
from app.modules.registration import router as registration_router
from app.modules.research import router as research_router
from app.modules.safety import router as safety_router
from app.modules.warehouse import router as warehouse_router
from app.modules.warehouse.reagent_api import router as reagent_router
from app.platform.system import router as system_router
from app.api.v1.ai_log_api import router as ai_log_router
from app.api.v1.ai_config_api import router as ai_config_router

api_router = APIRouter()

api_router.include_router(system_router, prefix="/system", tags=["系统"])
api_router.include_router(ai_log_router, prefix="", tags=["AI日志"])
api_router.include_router(ai_config_router, prefix="/ai", tags=["AI配置"])
api_router.include_router(production_router, prefix="/production", tags=["生产管理"])
api_router.include_router(equipment_router, prefix="/equipment", tags=["设备管理"])
api_router.include_router(safety_router, prefix="/safety", tags=["安全管理"])
api_router.include_router(environment_router, prefix="/environment", tags=["环保管理"])
api_router.include_router(energy_router, prefix="/energy", tags=["能源管理"])
api_router.include_router(warehouse_router, prefix="/warehouse", tags=["仓储管理"])
api_router.include_router(reagent_router, prefix="/reagent", tags=["试剂管理"])
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
api_router.include_router(sampling_router, prefix="/quality", tags=["取样管理"])
api_router.include_router(iqc_router, prefix="/quality", tags=["IQC检验"])
api_router.include_router(ipqc_router, prefix="/quality", tags=["IPQC检验"])
api_router.include_router(fqc_router, prefix="/quality", tags=["FQC检验"])
api_router.include_router(stability_router, prefix="/quality", tags=["稳定性试验管理"])
api_router.include_router(instrument_router, prefix="/quality", tags=["仪器校准管理"])
api_router.include_router(deviation_router, prefix="/quality", tags=["偏差管理"])
api_router.include_router(deviation_report_router, prefix="/quality", tags=["偏差报告"])
api_router.include_router(deviation_automation_router, prefix="/quality", tags=["偏差报告自动化"])
api_router.include_router(quality_reagent_router, prefix="/quality", tags=["质量检验-试剂管理"])
api_router.include_router(material_report_router, prefix="/quality", tags=["原料报告单"])
api_router.include_router(inspection_table_router, prefix="/quality", tags=["原料检验数据"])
