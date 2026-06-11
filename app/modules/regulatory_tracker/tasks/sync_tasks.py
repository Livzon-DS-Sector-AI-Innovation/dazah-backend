"""Background sync tasks — APScheduler integration."""

import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import async_session_factory
from app.modules.regulatory_tracker import repository as repo
from app.modules.regulatory_tracker.models import DataChannel, DataSource
from app.modules.regulatory_tracker.services.sync_service import run_sync_job

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def daily_sync_job():
    """每日定时同步任务：同步 CDE 国内药品技术指导原则前 1-3 页。"""
    logger.info("⏰ 开始每日同步任务 (daily_sync, pages 1-3)")

    try:
        async with async_session_factory() as db:
            source = await repo.get_data_source_by_code(db, "CDE")
            if not source:
                logger.error("CDE 数据源不存在，跳过同步")
                return

            channel = await repo.get_channel_by_code(db, source.id, "cde_domestic_guideline")
            if not channel:
                logger.error("cde_domestic_guideline 栏目不存在，跳过同步")
                return

            if not source.enabled or not channel.enabled:
                logger.info("数据源或栏目已禁用，跳过同步")
                return

            settings = get_settings()
            result = await run_sync_job(
                db=db,
                source=source,
                channel=channel,
                job_type="daily_sync",
                start_page=1,
                end_page=3,
                headless=settings.CRAWLER_HEADLESS,
            )

            logger.info(
                "✅ 每日同步完成: status=%s checked=%d new=%d updated=%d failed=%d error=%s",
                result["status"],
                result["checked"],
                result["new"],
                result["updated"],
                result["failed"],
                result.get("error"),
            )

    except Exception:
        logger.exception("❌ 每日同步任务异常")


def start_scheduler():
    """启动定时调度器。"""
    settings = get_settings()
    cron_expr = settings.DAILY_SYNC_CRON  # e.g. "0 2 * * *"

    parts = cron_expr.strip().split()
    if len(parts) != 5:
        logger.error("DAILY_SYNC_CRON 格式错误: %s，使用默认 0 2 * * *", cron_expr)
        parts = ["0", "2", "*", "*", "*"]

    trigger = CronTrigger(
        minute=parts[0],
        hour=parts[1],
        day=parts[2],
        month=parts[3],
        day_of_week=parts[4],
        timezone="Asia/Shanghai",
    )

    scheduler.add_job(
        daily_sync_job,
        trigger=trigger,
        id="daily_cde_sync",
        name="CDE 国内药品技术指导原则每日同步",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("📅 Scheduler 已启动, cron=%s (Asia/Shanghai)", cron_expr)


def stop_scheduler():
    """停止定时调度器。"""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("📅 Scheduler 已停止")
