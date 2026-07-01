"""Registration module test fixtures."""
from __future__ import annotations

import pytest


@pytest.fixture
def sample_drug_data():
    return {
        "drug_name": "阿莫西林",
        "generic_name": "Amoxicillin",
        "dosage_form": "胶囊剂",
        "specification": "0.5g",
    }


@pytest.fixture
def sample_authorization_data():
    return {
        "authorization_no": "AUTH-2026-001",
        "drug_id": None,  # Will be set in test
        "status": "pending",
    }
