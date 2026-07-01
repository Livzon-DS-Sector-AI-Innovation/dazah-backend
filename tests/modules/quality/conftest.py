"""Quality module test fixtures."""
from __future__ import annotations

import pytest


@pytest.fixture
def sample_deviation_data():
    return {
        "deviation_no": "DEV-2026-001",
        "title": "工艺参数偏差",
        "description": "反应温度超出规定范围",
        "severity": "major",
        "status": "open",
    }


@pytest.fixture
def sample_capa_data():
    return {
        "capa_no": "CAPA-2026-001",
        "title": "纠正措施：温度控制",
        "description": "实施温度监控改进措施",
        "type": "corrective",
        "status": "open",
    }
