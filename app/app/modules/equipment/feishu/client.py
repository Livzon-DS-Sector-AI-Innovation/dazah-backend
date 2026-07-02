"""设备模块飞书客户端.

业务: 设备模块飞书机器人客户端初始化（独立设备交互机器人凭证）
依赖: app.core.config (EQUIPMENT_FEISHU_APP_ID/SECRET)
"""

import json
import logging

import lark_oapi as lark

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


async def get_equipment_feishu_client() -> lark.Client:
    """获取设备模块飞书客户端（使用设备交互机器人凭证）."""
    return (
        lark.Client.builder()
        .app_id(settings.EQUIPMENT_FEISHU_APP_ID)
        .app_secret(settings.EQUIPMENT_FEISHU_APP_SECRET)
        .domain(lark.FEISHU_DOMAIN)
        .app_type(lark.AppType.SELF)
        .build()
    )


async def get_equipment_tenant_token(client: lark.Client) -> str:
    """获取设备机器人的 tenant_access_token."""
    from lark_oapi.api.auth.v3 import (
        InternalTenantAccessTokenRequest,
        InternalTenantAccessTokenRequestBody,
    )

    req = (
        InternalTenantAccessTokenRequest.builder()
        .request_body(
            InternalTenantAccessTokenRequestBody.builder()
            .app_id(settings.EQUIPMENT_FEISHU_APP_ID)
            .app_secret(settings.EQUIPMENT_FEISHU_APP_SECRET)
            .build()
        )
        .build()
    )
    resp = await client.auth.v3.tenant_access_token.ainternal(req)
    if not resp.success():
        raise RuntimeError(
            f"设备机器人 token 获取失败: code={resp.code}, msg={resp.msg}"
        )
    if resp.raw and resp.raw.content:
        data = json.loads(resp.raw.content.decode("utf-8"))
        token = data.get("tenant_access_token", "")
        if token:
            return token
    raise RuntimeError("设备机器人 token 响应为空")


# 向后兼容别名（XBJ 现有 notification.py 引用 get_feishu_tenant_token）
get_feishu_tenant_token = get_equipment_tenant_token
