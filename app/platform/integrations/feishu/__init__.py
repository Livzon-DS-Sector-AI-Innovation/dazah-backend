"""Feishu SSO, approval, IM, Bitable, notification and WebSocket integrations."""

from app.platform.integrations.feishu.bitable import FeishuBitableSync
from app.platform.integrations.feishu.client import FeishuClient
from app.platform.integrations.feishu.datasource import BitableDataSource
from app.platform.integrations.feishu.employee_datasource import EmployeeBitableDataSource, EmployeeRecord
from app.platform.integrations.feishu.notification import (
    build_card,
    send_user_card,
)
from app.platform.integrations.feishu.ws_client import (
    start_ws_client,
    stop_ws_client,
)

__all__ = [
    "FeishuClient",
    "FeishuBitableSync",
    "BitableDataSource",
    "EmployeeBitableDataSource",
    "EmployeeRecord",
    "build_card",
    "send_user_card",
    "start_ws_client",
    "stop_ws_client",
]
