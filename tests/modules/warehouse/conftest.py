"""Warehouse module test fixtures."""
from __future__ import annotations

import pytest


@pytest.fixture
def sample_inventory_data():
    return {
        "material_code": "MAT-001",
        "material_name": "原料药A",
        "quantity": 100.0,
        "unit": "kg",
        "warehouse": "原料仓库A",
        "batch_no": "BATCH-2026-001",
    }
