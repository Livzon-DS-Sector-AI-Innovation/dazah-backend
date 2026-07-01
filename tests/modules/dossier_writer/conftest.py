"""Dossier writer module test fixtures."""
from __future__ import annotations

import pytest


@pytest.fixture
def sample_dossier_data():
    return {
        "title": "阿莫西林注册资料",
        "product_name": "阿莫西林",
        "status": "draft",
    }
