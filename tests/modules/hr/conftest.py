"""HR module test fixtures."""
from __future__ import annotations

import pytest


@pytest.fixture
def sample_employee_data():
    return {
        "employee_number": "EMP-001",
        "name": "张三",
        "department": "生产部",
        "position": "工艺工程师",
        "status": "active",
    }
