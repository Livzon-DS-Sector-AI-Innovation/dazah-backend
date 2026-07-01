"""Production module test fixtures."""
from __future__ import annotations

import pytest


@pytest.fixture
def sample_batch_data():
    return {
        "batch_no": "BATCH-2026-001",
        "product_name": "阿莫西林",
        "batch_size": 100.0,
        "unit": "kg",
        "status": "draft",
    }


@pytest.fixture
def sample_production_plan_data():
    return {
        "plan_no": "PLAN-2026-001",
        "product_name": "阿莫西林",
        "planned_quantity": 500.0,
        "unit": "kg",
        "planned_start_date": "2026-07-01",
        "planned_end_date": "2026-07-15",
    }
