import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from pathlib import Path

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import AppException
from app.core.response import error_response
from app.platform.audit import AuditMiddleware

settings = get_settings()

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting %s (%s)", settings.APP_NAME, settings.APP_ENV)

    # 启动时从数据库加载 AI 配置
    try:
        from app.core.ai_config import load_config_from_db
        await load_config_from_db()
        logger.info("AI config loaded from database")
    except Exception as e:
        logger.warning(f"Failed to load AI config from database: {e}")

    # 启动试剂提醒调度器
    try:
        from app.modules.quality.reagent_reminder_scheduler import start_reagent_reminder_scheduler
        start_reagent_reminder_scheduler()
        logger.info("Reagent reminder scheduler started")
    except Exception as e:
        logger.warning(f"Failed to start reagent reminder scheduler: {e}")

    # 启动偏差填报人提醒调度器
    try:
        from app.modules.quality.deviation_reporter_reminder_scheduler import start_deviation_reporter_reminder_scheduler
        start_deviation_reporter_reminder_scheduler()
        logger.info("Deviation reporter reminder scheduler started")
    except Exception as e:
        logger.warning(f"Failed to start deviation reporter reminder scheduler: {e}")

    yield
    logger.info("Shutting down %s", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    description="原料药事业部工厂基座系统",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

# 添加 CORS 中间件
# 生产环境允许所有来源，开发环境限制 localhost
if settings.is_production:
    # 生产环境允许所有来源
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # 开发环境限制 localhost
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_middleware(AuditMiddleware)

# 添加静态文件服务（支持上传文件访问）
uploads_dir = Path("uploads")
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return error_response(
        message=exc.message,
        detail=exc.detail_msg,
        status_code=exc.status_code,
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    return error_response(
        message=str(exc.detail),
        status_code=exc.status_code,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = exc.errors()
    # 打印完整错误信息以便调试
    logger.error(f"Validation error: {errors}")
    detail = "; ".join(
        f"{e.get('loc', [''])[-1]}: {e.get('msg', '')}" for e in errors
    )
    return error_response(
        message="请求参数校验失败",
        detail=detail,
        status_code=422,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return error_response(
        message=f"服务器内部错误: {str(exc)}",
        status_code=500,
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
