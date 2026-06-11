"""维修人员 API 路由."""

import logging

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.database import get_db
from app.core.response import success_response
from app.platform.identity.models import User

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/maintainers", summary="获取设备部维修人员列表")
async def list_maintainers(
    settings: Settings = Depends(get_settings),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    dept_id = settings.FEISHU_EQUIPMENT_DEPT_ID
    if not dept_id:
        return success_response(data=[])

    from app.platform.integrations.feishu.contact import get_department_members

    members = await get_department_members(dept_id)

    # 将飞书 user_id 映射为本地 User.id (UUID)
    feishu_ids = [m["user_id"] for m in members if m.get("user_id")]
    id_map: dict[str, str] = {}
    if feishu_ids:
        result = await db.execute(
            select(User.id, User.feishu_user_id).where(
                User.feishu_user_id.in_(feishu_ids)
            )
        )
        id_map = {row.feishu_user_id: str(row.id) for row in result.all()}

    # 返回本地 UUID 作为 user_id，前端直接用作 responsible_person_id
    mapped = []
    for m in members:
        fid = m.get("user_id", "")
        local_id = id_map.get(fid)
        if local_id:
            mapped.append({
                "user_id": local_id,
                "name": m.get("name", ""),
                "employee_no": m.get("employee_no", ""),
                "department_id": m.get("department_id", ""),
            })
        else:
            logger.warning(
                "Maintainer %s (feishu_user_id=%s) not found in local users",
                m.get("name"), fid,
            )

    return success_response(data=mapped)
