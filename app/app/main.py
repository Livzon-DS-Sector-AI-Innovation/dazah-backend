import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import AppException
from app.core.response import error_response
from app.platform.audit import AuditMiddleware

# Ensure platform models are registered in SQLAlchemy metadata
import app.platform.identity.models  # noqa: F401
import app.platform.audit.models  # noqa: F401

settings = get_settings()

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    import asyncio

    logger.info("Starting %s (%s)", settings.APP_NAME, settings.APP_ENV)

    # ── 安全模块专属飞书事件订阅（WebSocket 长连接，独立应用凭据）──
    # 未配置 SAFETY_FEISHU_APP_ID/SECRET 时 start_ws 内部自动跳过，不阻断启动
    from app.modules.safety.feishu.event_client import start_ws, stop_ws

    safety_ws_task = asyncio.create_task(start_ws())

    # ── 安全模块定时任务调度引擎 ──
    from app.modules.safety.scheduler import (
        scheduled_task_loop,
        stop_scheduled_task_flag,
    )

    scheduler_task = asyncio.create_task(scheduled_task_loop())

    logger.info("Background tasks started")

    yield

    # 停止安全模块 WebSocket
    await stop_ws()
    safety_ws_task.cancel()

    # 停止定时任务调度引擎
    stop_scheduled_task_flag.set()
    scheduler_task.cancel()

    logger.info("Shutting down %s", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    description="原料药事业部工厂基座系统",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuditMiddleware)

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
    detail = "; ".join(
        f"{e.get('loc', [''])[-1]}: {e.get('msg', '')}" for e in errors
    )
    return error_response(
        message="请求参数校验失败",
        detail=detail,
        status_code=422,
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
