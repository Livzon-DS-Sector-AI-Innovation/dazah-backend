"""Feishu SSO, approval, IM, Bitable, notification and WebSocket integrations."""

from app.platform.integrations.feishu.bitable import FeishuBitableSync
from app.platform.integrations.feishu.client import FeishuClient
from app.platform.integrations.feishu.datasource import BitableDataSource
from app.platform.integrations.feishu.employee_datasource import (
    EmployeeBitableDataSource,
    EmployeeRecord,
)
from app.platform.integrations.feishu.notification import (
    build_card,
    send_user_card,
)
from app.platform.integrations.feishu.utils import (
    FEISHU_BITABLE_RECORD_CHANGED_EVENT,
    BitableReference,
    ConnectivityStep,
    get_tenant_access_token,
    normalize_app_token,
    normalize_table_id,
    parse_bitable_url,
    test_bitable_table,
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
    "BitableReference",
    "ConnectivityStep",
    "FEISHU_BITABLE_RECORD_CHANGED_EVENT",
    "get_tenant_access_token",
    "normalize_app_token",
    "normalize_table_id",
    "parse_bitable_url",
    "test_bitable_table",
    "start_ws_client",
    "stop_ws_client",
]
