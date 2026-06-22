"""Feishu-to-local-DB sync orchestration.

Provides:
- `run_sync`: generic ETL helper (fetch → parse → upsert → stats)
- `sync_departments`: sync org structure from Feishu
- `sync_members`: sync members from a target department
"""

import json
import logging
import time
from typing import Any, Callable, Coroutine

from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import async_session_factory

logger = logging.getLogger(__name__)

SyncStats = dict[str, int]


async def run_sync(
    *,
    fetch_records: Callable[[], Coroutine[Any, Any, list[dict]]],
    parse_record: Callable[[dict], dict | None],
    upsert_record: Callable[[dict], Coroutine[Any, Any, None]],
    get_existing: Callable[[str], Coroutine[Any, Any, Any | None]],
    get_record_id: Callable[[dict], str | None],
    post_process: Callable[[Any, dict], Coroutine[Any, Any, None]] | None = None,
) -> SyncStats:
    """Generic sync orchestrator: fetch -> parse -> upsert -> stats.

    Args:
        fetch_records: Coroutine that returns raw Feishu record dicts.
        parse_record: Callable that converts a raw record to local DB kwargs
                      (returns None to skip).
        upsert_record: Coroutine that writes/updates the local DB record.
        get_existing: Coroutine that fetches the local DB record by its key
                      (used to distinguish created vs updated).
        get_record_id: Callable that extracts the unique key from parsed data.
        post_process: Optional coroutine called after a successful upsert,
                      receiving (existing_record, parsed_data).

    Returns:
        {"created": int, "updated": int, "failed": int, "total": int}
    """
    raw_records = await fetch_records()
    stats: SyncStats = {"created": 0, "updated": 0, "failed": 0, "total": len(raw_records)}

    for rec in raw_records:
        try:
            parsed = parse_record(rec)
            if not parsed:
                stats["failed"] += 1
                continue

            rid = get_record_id(parsed)
            if not rid:
                stats["failed"] += 1
                continue

            await upsert_record(parsed)

            existing = await get_existing(rid)
            if existing and existing.created_at and _is_newly_created(existing):
                stats["created"] += 1
            else:
                stats["updated"] += 1

            if post_process:
                await post_process(existing, parsed)

        except Exception:
            logger.exception("Failed to sync Feishu record %s", rec.get("record_id"))
            stats["failed"] += 1

    return stats


def _is_newly_created(existing: Any) -> bool:
    """Heuristic: record created within last 60 seconds -> treat as 'created'."""
    from datetime import datetime, timezone

    created_at = existing.created_at
    if not created_at:
        return False
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - created_at).total_seconds() < 60


# ── Department sync ─────────────────────────────────────────────────


async def sync_departments(root_dept_id: str) -> dict:
    """Sync department structure from Feishu starting at root_dept_id.

    Uses BFS to fetch all departments under root, then upserts into
    identity.departments table.

    Returns stats dict with dept_count, elapsed.
    """
    from app.platform.identity.models import Department
    from app.platform.integrations.feishu.contact import get_all_departments

    t0 = time.time()
    logger.info("sync_departments starting (root=%s)", root_dept_id)

    async def fetch_depts() -> list[dict]:
        return await get_all_departments()

    def parse_dept(rec: dict) -> dict | None:
        dept_id = rec.get("department_id")
        if not dept_id:
            return None
        return {
            "department_id": dept_id,
            "name": rec.get("name", ""),
            "parent_department_id": rec.get("parent_department_id", ""),
            "leader_user_id": rec.get("leader_user_id", ""),
            "member_count": rec.get("member_count", 0),
            "status_is_deleted": rec.get("status_is_deleted", False),
            "order": rec.get("order", 0),
        }

    async def upsert_dept(parsed: dict) -> None:
        async with async_session_factory() as db:
            result = await db.execute(
                select(Department).where(
                    Department.feishu_department_id == parsed["department_id"]
                )
            )
            existing = result.scalar_one_or_none()
            if existing:
                existing.name = parsed["name"]
                existing.parent_feishu_department_id = parsed["parent_department_id"]
                existing.leader_user_id = parsed["leader_user_id"]
                existing.member_count = parsed["member_count"]
                existing.status_is_deleted = parsed["status_is_deleted"]
                existing.order = parsed["order"]
            else:
                db.add(Department(
                    feishu_department_id=parsed["department_id"],
                    name=parsed["name"],
                    parent_feishu_department_id=parsed["parent_department_id"],
                    leader_user_id=parsed["leader_user_id"],
                    member_count=parsed["member_count"],
                    status_is_deleted=parsed["status_is_deleted"],
                    order=parsed["order"],
                ))
            await db.commit()

    async def get_existing(dept_id: str):
        async with async_session_factory() as db:
            result = await db.execute(
                select(Department).where(
                    Department.feishu_department_id == dept_id
                )
            )
            return result.scalar_one_or_none()

    stats = await run_sync(
        fetch_records=fetch_depts,
        parse_record=parse_dept,
        upsert_record=upsert_dept,
        get_existing=get_existing,
        get_record_id=lambda r: r["department_id"],
    )

    elapsed = time.time() - t0
    logger.info(
        "sync_departments done: %d depts (%d created, %d updated) in %.1fs",
        stats["total"], stats["created"], stats["updated"], elapsed,
    )
    return {"dept_count": stats["total"], "elapsed": round(elapsed, 1)}


# ── Member sync ─────────────────────────────────────────────────────


async def sync_members(target_dept_id: str) -> dict:
    """Sync all members under target_dept_id from Feishu.

    BFS fetches all departments under target, then fetches all users
    from each department, and upserts into identity.users table.

    Returns stats dict with user_count, dept_count, elapsed.
    """
    from app.platform.identity.models import User
    from app.platform.integrations.feishu.contact import (
        get_all_departments,
        find_users_by_department,
    )

    t0 = time.time()
    logger.info("sync_members starting (target=%s)", target_dept_id)

    # Get all departments under target
    all_depts = await get_all_departments()
    # Filter to only those under target (simple: include all for now)
    dept_ids = [d["department_id"] for d in all_depts]

    async def fetch_users() -> list[dict]:
        """Fetch all users from all departments."""
        all_users = []
        for dept_id in dept_ids:
            try:
                users = await find_users_by_department(dept_id)
                # Add dept_name to each user
                dept_name = next(
                    (d["name"] for d in all_depts if d["department_id"] == dept_id),
                    "",
                )
                for u in users:
                    u["dept_name"] = dept_name
                    u["dept_id"] = dept_id
                all_users.extend(users)
            except Exception:
                logger.exception("Failed to fetch users from dept %s", dept_id)
        return all_users

    def parse_user(rec: dict) -> dict | None:
        open_id = rec.get("open_id")
        if not open_id:
            return None
        # Build department_ids JSON
        dept_ids = rec.get("department_ids", [])
        dept_ids_json = json.dumps(dept_ids) if dept_ids else None
        return {
            "open_id": open_id,
            "user_id": rec.get("user_id", ""),
            "name": rec.get("name", ""),
            "en_name": rec.get("en_name", ""),
            "employee_no": rec.get("employee_no") or None,
            "email": rec.get("email") or None,
            "mobile": rec.get("mobile") or None,
            "department": rec.get("dept_name", ""),
            "position": rec.get("job_title") or None,
            "avatar_url": rec.get("avatar_key") or None,
            "feishu_department_ids": dept_ids_json,
        }

    async def upsert_user(parsed: dict) -> None:
        async with async_session_factory() as db:
            result = await db.execute(
                select(User).where(User.feishu_open_id == parsed["open_id"])
            )
            existing = result.scalar_one_or_none()
            if existing:
                existing.name = parsed["name"] or existing.name
                existing.en_name = parsed["en_name"] or existing.en_name
                existing.employee_no = parsed["employee_no"] or existing.employee_no
                existing.email = parsed["email"] or existing.email
                existing.mobile = parsed["mobile"] or existing.mobile
                existing.position = parsed["position"] or existing.position
                existing.avatar_url = parsed["avatar_url"] or existing.avatar_url
                if not existing.department:
                    existing.department = parsed["department"]
                existing.feishu_department_ids = parsed["feishu_department_ids"]
                if not existing.feishu_user_id:
                    existing.feishu_user_id = parsed["user_id"]
            else:
                db.add(User(
                    name=parsed["name"],
                    en_name=parsed["en_name"],
                    feishu_user_id=parsed["user_id"],
                    feishu_open_id=parsed["open_id"],
                    employee_no=parsed["employee_no"],
                    email=parsed["email"],
                    mobile=parsed["mobile"],
                    department=parsed["department"],
                    position=parsed["position"],
                    avatar_url=parsed["avatar_url"],
                    feishu_department_ids=parsed["feishu_department_ids"],
                ))
            await db.commit()

    async def get_existing(open_id: str):
        async with async_session_factory() as db:
            result = await db.execute(
                select(User).where(User.feishu_open_id == open_id)
            )
            return result.scalar_one_or_none()

    stats = await run_sync(
        fetch_records=fetch_users,
        parse_record=parse_user,
        upsert_record=upsert_user,
        get_existing=get_existing,
        get_record_id=lambda r: r["open_id"],
    )

    elapsed = time.time() - t0
    logger.info(
        "sync_members done: %d users from %d depts (%d created, %d updated) in %.1fs",
        stats["total"], len(dept_ids), stats["created"], stats["updated"], elapsed,
    )
    return {
        "user_count": stats["total"],
        "dept_count": len(dept_ids),
        "elapsed": round(elapsed, 1),
    }
