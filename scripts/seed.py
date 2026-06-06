"""Seed script: import departments and teams from JSON files."""

import asyncio
import json
import sys
from pathlib import Path
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Allow running from project root or scripts/ dir
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import get_settings
from app.modules.hr.models import Department, Team

settings = get_settings()
engine = create_async_engine(settings.DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

DATA_DIR = PROJECT_ROOT


async def seed_departments(session: AsyncSession) -> dict[str, UUID]:
    """Import departments.json and return name->id mapping."""
    with open(DATA_DIR / "departments.json", encoding="utf-8") as f:
        data = json.load(f)

    # Check existing departments to avoid duplicates
    result = await session.execute(select(Department.name, Department.id))
    existing = {name: id_ for name, id_ in result.all()}
    dept_map = dict(existing)

    inserted = 0
    for item in data:
        name = item["name"]
        if name in dept_map:
            continue
        dept = Department(
            id=UUID(item["id"]),
            name=name,
            code=item["code"],
        )
        session.add(dept)
        dept_map[name] = UUID(item["id"])
        inserted += 1

    await session.commit()
    print(f"  Departments: {inserted} inserted, {len(existing)} already exist.")
    return dept_map


async def seed_teams(session: AsyncSession, dept_map: dict[str, UUID]) -> None:
    """Import teams.json linked to departments."""
    with open(DATA_DIR / "teams.json", encoding="utf-8") as f:
        data = json.load(f)

    # Check existing teams
    result = await session.execute(select(Team.name, Team.department_id))
    existing = {(name, dept_id) for name, dept_id in result.all()}

    inserted = 0
    for item in data:
        dept_name = item["department"]
        team_name = item["team"]
        dept_id = dept_map.get(dept_name)
        if dept_id is None:
            print(f"  Warning: department '{dept_name}' not found, skipping team '{team_name}'.")
            continue
        if (team_name, dept_id) in existing:
            continue
        team = Team(
            name=team_name,
            department_id=dept_id,
        )
        session.add(team)
        inserted += 1

    await session.commit()
    print(f"  Teams: {inserted} inserted, {len(existing)} already exist.")


async def main() -> None:
    print("Seeding database...")
    async with async_session() as session:
        dept_map = await seed_departments(session)
        await seed_teams(session, dept_map)
    print("Done.")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
