"""巡检飞书交互会话管理 — 基于 Redis 的待确认结果暂存。

每个用户（open_id）最多有一个活跃会话，
存储 AI 分析结果，等待用户确认/修改后提交。
"""

import json
import logging

from app.core.redis import cache_delete, cache_get, cache_set

logger = logging.getLogger(__name__)

_SESSION_PREFIX = "inspection:session:"
_SESSION_TTL = 1800  # 30 分钟


def _session_key(open_id: str) -> str:
    return f"{_SESSION_PREFIX}{open_id}"


async def save_session(
    open_id: str,
    *,
    task_id: str,
    equipment_id: str,
    task_no: str,
    equipment_name: str,
    results: list[dict],
) -> None:
    """保存巡检待确认会话（覆盖旧会话）。"""
    data = {
        "task_id": task_id,
        "equipment_id": equipment_id,
        "task_no": task_no,
        "equipment_name": equipment_name,
        "results": results,
    }
    await cache_set(
        _session_key(open_id),
        json.dumps(data, ensure_ascii=False),
        ex=_SESSION_TTL,
    )
    logger.info("巡检会话已保存: open_id=%s, task=%s", open_id, task_no)


async def get_session(open_id: str) -> dict | None:
    """读取巡检待确认会话，不存在返回 None。"""
    raw = await cache_get(_session_key(open_id))
    if raw is None:
        return None
    try:
        return json.loads(raw)  # type: ignore[return-value]
    except (json.JSONDecodeError, TypeError):
        logger.warning("巡检会话数据损坏: open_id=%s", open_id)
        await clear_session(open_id)
        return None


async def update_results(open_id: str, results: list[dict]) -> bool:
    """更新会话中的检查结果，会话不存在返回 False。"""
    session = await get_session(open_id)
    if session is None:
        return False
    session["results"] = results
    await cache_set(
        _session_key(open_id),
        json.dumps(session, ensure_ascii=False),
        ex=_SESSION_TTL,
    )
    logger.info("巡检会话结果已更新: open_id=%s", open_id)
    return True


async def clear_session(open_id: str) -> None:
    """清除巡检待确认会话。"""
    await cache_delete(_session_key(open_id))
    logger.info("巡检会话已清除: open_id=%s", open_id)
