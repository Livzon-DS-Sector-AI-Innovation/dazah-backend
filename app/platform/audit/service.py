import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.platform.audit.models import AuditLog


async def record_audit_log(
    db: AsyncSession,
    *,
    action: str,
    request_id: str | None = None,
    user_id: uuid.UUID | None = None,
    resource_type: str | None = None,
    resource_id: uuid.UUID | None = None,
    old_value: dict[str, Any] | None = None,
    new_value: dict[str, Any] | None = None,
    extra: dict[str, Any] | None = None,
) -> AuditLog:
    audit_log = AuditLog(
        request_id=request_id,
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        old_value=old_value,
        new_value=new_value,
        extra=extra,
    )
    db.add(audit_log)
    await db.flush()
    return audit_log
