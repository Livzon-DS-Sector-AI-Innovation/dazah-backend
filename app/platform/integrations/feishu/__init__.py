"""Feishu SSO, approval, IM and Bitable integration."""

from app.platform.integrations.feishu.bitable import FeishuBitableSync
from app.platform.integrations.feishu.candidate_datasource import (
    CandidateBitableDataSource,
    CandidateRecord,
)
from app.platform.integrations.feishu.client import FeishuClient
from app.platform.integrations.feishu.datasource import BitableDataSource
from app.platform.integrations.feishu.employee_datasource import EmployeeBitableDataSource, EmployeeRecord

__all__ = [
    "CandidateBitableDataSource",
    "CandidateRecord",
    "FeishuClient",
    "FeishuBitableSync",
    "BitableDataSource",
    "EmployeeBitableDataSource",
    "EmployeeRecord",
]
