"""Feishu message push service.

业务: 向飞书群聊/用户推送卡片消息（工单、巡检等通知）
依赖: 主飞书机器人凭证 (FEISHU_APP_ID/SECRET, 见 app.core.config)
"""

import json
import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


async def _get_feishu_client():
    import lark_oapi as lark

    return (
        lark.Client.builder()
        .app_id(settings.FEISHU_APP_ID)
        .app_secret(settings.FEISHU_APP_SECRET)
        .domain(lark.FEISHU_DOMAIN)
        .app_type(lark.AppType.SELF)
        .build()
    )


async def _get_tenant_token(client) -> str:
    import json as _json

    from lark_oapi.api.auth.v3 import (
        InternalTenantAccessTokenRequest,
        InternalTenantAccessTokenRequestBody,
    )

    req = (
        InternalTenantAccessTokenRequest.builder()
        .request_body(
            InternalTenantAccessTokenRequestBody.builder()
            .app_id(settings.FEISHU_APP_ID)
            .app_secret(settings.FEISHU_APP_SECRET)
            .build()
        )
        .build()
    )
    resp = await client.auth.v3.tenant_access_token.ainternal(req)
    if not resp.success():
        raise RuntimeError(
            f"Failed to get tenant token: code={resp.code}, msg={resp.msg}",
        )
    if resp.raw and resp.raw.content:
        data = _json.loads(resp.raw.content.decode("utf-8"))
        return data.get("tenant_access_token", "")
    raise RuntimeError("Empty tenant token response")


async def send_group_card(
    chat_id: str,
    title: str,
    content: str,
    elements: list[dict] | None = None,
) -> bool:
    """发送卡片消息到群聊"""
    try:
        client = await _get_feishu_client()
        token = await _get_tenant_token(client)

        from lark_oapi.api.im.v1 import (
            CreateMessageRequest,
            CreateMessageRequestBody,
        )

        card = {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": "orange",
            },
            "elements": [
                {"tag": "markdown", "content": content},
            ],
        }
        if elements:
            card["elements"].extend(elements)

        card_json = json.dumps(card, ensure_ascii=False)

        req = (
            CreateMessageRequest.builder()
            .receive_id_type("chat_id")
            .request_body(
                CreateMessageRequestBody.builder()
                .receive_id(chat_id)
                .msg_type("interactive")
                .content(card_json)
                .build()
            )
            .build()
        )
        req.headers["Authorization"] = f"Bearer {token}"
        resp = await client.im.v1.message.acreate(req)
        if not resp.success():
            logger.error("Failed to send card message: %s", resp.msg)
            return False
        return True
    except Exception:
        logger.exception("send_group_card failed")
        return False
