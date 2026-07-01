"""Safety module model tests."""
from __future__ import annotations

import pytest
from sqlalchemy import select

from app.modules.safety.models import Hazard


@pytest.mark.asyncio
async def test_hazard_model_creation(db_session, sample_hazard_data):
    hazard = Hazard(**sample_hazard_data)
    db_session.add(hazard)
    await db_session.commit()

    result = await db_session.execute(select(Hazard).where(Hazard.id == hazard.id))
    fetched = result.scalar_one()
    assert fetched.hazard_no == "HAZ-2026-001"
    assert fetched.risk_level == 2
    assert fetched.status == "open"
