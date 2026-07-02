"""设备模块飞书通知.

业务: 设备巡检、工单等飞书卡片消息通知
依赖: app.modules.equipment.feishu.client
"""

import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


async def send_inspection_task_card(
    feishu_user_id: str,
    task_no: str,
    task_type: str,
    equipment_name: str,
    planned_time: datetime,
    route_name: str | None = None,
) -> bool:
    """发送巡检任务卡片通知.

    Args:
        feishu_user_id: 飞书用户ID
        task_no: 任务编号
        task_type: 任务类型(线路巡检/设备巡检)
        equipment_name: 设备名称
        planned_time: 计划巡检时间
        route_name: 巡检路线名称(可选)

    Returns:
        True表示发送成功
    """
    try:
        from app.modules.equipment.feishu.client import (
            get_equipment_feishu_client,
            get_feishu_tenant_token,
        )

        client = await get_equipment_feishu_client()
        token = await get_feishu_tenant_token(client)

        from lark_oapi.api.im.v1 import (
            CreateMessageRequest,
            CreateMessageRequestBody,
        )

        # 构建卡片内容
        planned_time_str = planned_time.strftime("%Y-%m-%d %H:%M") if planned_time else "未指定"

        card = {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": "🔧 新的巡检任务"},
                "template": "orange",
            },
            "elements": [
                {"tag": "div", "text": {"tag": "lark_md", "content": f"**任务编号:** {task_no}"}},
                {"tag": "div", "text": {"tag": "lark_md", "content": f"**巡检类型:** {task_type}"}},
                {"tag": "div", "text": {"tag": "lark_md", "content": f"**设备名称:** {equipment_name}"}},
                {"tag": "div", "text": {"tag": "lark_md", "content": f"**计划时间:** {planned_time_str}"}},
            ],
        }

        if route_name:
            card["elements"].insert(
                2,
                {"tag": "div", "text": {"tag": "lark_md", "content": f"**巡检路线:** {route_name}"}}
            )

        # 添加操作按钮
        card["elements"].append({"tag": "hr"})
        card["elements"].append({
            "tag": "action",
            "actions": [
                {
                    "tag": "button",
                    "text": {"tag": "plain_text", "content": "查看详情"},
                    "type": "primary",
                    "url": f"http://localhost:3000/equipment/inspection/tasks",
                }
            ],
        })

        card_json = json.dumps(card, ensure_ascii=False)

        req = (
            CreateMessageRequest.builder()
            .receive_id_type("user_id")
            .request_body(
                CreateMessageRequestBody.builder()
                .receive_id(feishu_user_id)
                .msg_type("interactive")
                .content(card_json)
                .build()
            )
            .build()
        )
        req.headers["Authorization"] = f"Bearer {token}"

        resp = await client.im.v1.message.acreate(req)
        if not resp.success():
            logger.error(
                "发送巡检任务卡片失败: user_id=%s, code=%s, msg=%s",
                feishu_user_id, resp.code, resp.msg
            )
            return False

        logger.info("巡检任务卡片已发送: user_id=%s, task_no=%s", feishu_user_id, task_no)
        return True

    except Exception as e:
        logger.exception("发送巡检任务卡片异常: user_id=%s", feishu_user_id)
        return False


async def send_work_order_card(
    feishu_user_id: str,
    work_order_no: str,
    order_type: str,
    equipment_name: str,
    priority: str,
    fault_description: str | None = None,
) -> bool:
    """发送维修工单卡片通知.

    Args:
        feishu_user_id: 飞书用户ID
        work_order_no: 工单编号
        order_type: 工单类型
        equipment_name: 设备名称
        priority: 优先级
        fault_description: 故障描述

    Returns:
        True表示发送成功
    """
    try:
        from app.modules.equipment.feishu.client import (
            get_equipment_feishu_client,
            get_feishu_tenant_token,
        )

        client = await get_equipment_feishu_client()
        token = await get_feishu_tenant_token(client)

        from lark_oapi.api.im.v1 import (
            CreateMessageRequest,
            CreateMessageRequestBody,
        )

        # 根据优先级设置颜色
        template_color = {"紧急": "red", "高": "orange", "中": "yellow", "低": "green"}.get(priority, "blue")

        card = {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": "🔨 新的维修工单"},
                "template": template_color,
            },
            "elements": [
                {"tag": "div", "text": {"tag": "lark_md", "content": f"**工单编号:** {work_order_no}"}},
                {"tag": "div", "text": {"tag": "lark_md", "content": f"**工单类型:** {order_type}"}},
                {"tag": "div", "text": {"tag": "lark_md", "content": f"**设备名称:** {equipment_name}"}},
                {"tag": "div", "text": {"tag": "lark_md", "content": f"**优先级:** {priority}"}},
            ],
        }

        if fault_description:
            card["elements"].append(
                {"tag": "div", "text": {"tag": "lark_md", "content": f"**故障描述:** {fault_description}"}}
            )

        card["elements"].append({"tag": "hr"})
        card["elements"].append({
            "tag": "action",
            "actions": [
                {
                    "tag": "button",
                    "text": {"tag": "plain_text", "content": "查看详情"},
                    "type": "primary",
                    "url": f"http://localhost:3000/equipment/maintenance",
                }
            ],
        })

        card_json = json.dumps(card, ensure_ascii=False)

        req = (
            CreateMessageRequest.builder()
            .receive_id_type("user_id")
            .request_body(
                CreateMessageRequestBody.builder()
                .receive_id(feishu_user_id)
                .msg_type("interactive")
                .content(card_json)
                .build()
            )
            .build()
        )
        req.headers["Authorization"] = f"Bearer {token}"

        resp = await client.im.v1.message.acreate(req)
        if not resp.success():
            logger.error(
                "发送工单卡片失败: user_id=%s, code=%s, msg=%s",
                feishu_user_id, resp.code, resp.msg
            )
            return False

        logger.info("工单卡片已发送: user_id=%s, work_order_no=%s", feishu_user_id, work_order_no)
        return True

    except Exception as e:
        logger.exception("发送工单卡片异常: user_id=%s", feishu_user_id)
        return False


async def send_text_message(
    feishu_user_id: str,
    content: str,
) -> bool:
    """发送纯文本消息.

    Args:
        feishu_user_id: 飞书用户ID
        content: 消息内容

    Returns:
        True表示发送成功
    """
    try:
        from app.modules.equipment.feishu.client import (
            get_equipment_feishu_client,
            get_feishu_tenant_token,
        )

        client = await get_equipment_feishu_client()
        token = await get_feishu_tenant_token(client)

        from lark_oapi.api.im.v1 import (
            CreateMessageRequest,
            CreateMessageRequestBody,
        )

        req = (
            CreateMessageRequest.builder()
            .receive_id_type("user_id")
            .request_body(
                CreateMessageRequestBody.builder()
                .receive_id(feishu_user_id)
                .msg_type("text")
                .content(json.dumps({"text": content}, ensure_ascii=False))
                .build()
            )
            .build()
        )
        req.headers["Authorization"] = f"Bearer {token}"

        resp = await client.im.v1.message.acreate(req)
        if not resp.success():
            logger.error(
                "发送文本消息失败: user_id=%s, code=%s, msg=%s",
                feishu_user_id, resp.code, resp.msg
            )
            return False

        logger.info("文本消息已发送: user_id=%s", feishu_user_id)
        return True

    except Exception as e:
        logger.exception("发送文本消息异常: user_id=%s", feishu_user_id)
        return False


async def send_user_card(
    open_id: str,
    title: str,
    content: str,
    elements: list[dict] | None = None,
    receive_id_type: str = "user_id",
) -> bool:
    """使用设备机器人发送卡片消息给单个用户（DM）。

    Args:
        open_id: 接收者标识（含义由 receive_id_type 决定）
        title: 卡片标题
        content: 卡片正文（支持 markdown）
        elements: 额外的卡片元素
        receive_id_type: 接收者 ID 类型，"user_id" 或 "open_id"

    Returns:
        True 表示发送成功，False 表示失败
    """
    logger.info(
        "设备机器人 send_user_card: %s=%s", receive_id_type, open_id,
    )
    try:
        from app.modules.equipment.feishu.client import (
            get_equipment_feishu_client,
            get_equipment_tenant_token,
        )

        client = await get_equipment_feishu_client()
        token = await get_equipment_tenant_token(client)

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
            .receive_id_type(receive_id_type)
            .request_body(
                CreateMessageRequestBody.builder()
                .receive_id(open_id)
                .msg_type("interactive")
                .content(card_json)
                .build()
            )
            .build()
        )
        req.headers["Authorization"] = f"Bearer {token}"
        resp = await client.im.v1.message.acreate(req)
        if not resp.success():
            logger.error(
                "设备机器人 send_user_card 失败: user_id=%s, code=%s, msg=%s",
                open_id, resp.code, resp.msg,
            )
            return False
        logger.info("设备机器人卡片已发送: user_id=%s, title=%s", open_id, title)
        return True
    except Exception as e:
        logger.error(
            "设备机器人 send_user_card 异常: user_id=%s, %s: %s",
            open_id, type(e).__name__, e,
        )
        return False
