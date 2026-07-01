"""Product module test fixtures."""
from __future__ import annotations

import pytest


@pytest.fixture
def sample_product_data():
    return {
        "product_code": "PROD-001",
        "product_name": "阿莫西林胶囊",
        "specification": "0.5g",
        "dosage_form": "胶囊剂",
    }
