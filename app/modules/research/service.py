"""Research business workflows."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateException, NotFoundException
from app.modules.research import repository as repo
from app.modules.research.models import ResearchProject
from app.modules.research.schemas import (
    ResearchProjectCreate,
    ResearchProjectUpdate,
)


async def create_project(
    db: AsyncSession, data: ResearchProjectCreate
) -> ResearchProject:
    if await repo.exists_by_project_no(db, data.project_no):
        raise DuplicateException("项目编号", data.project_no)
    return await repo.create_project(db, data.model_dump())


async def get_project(db: AsyncSession, project_id: uuid.UUID) -> ResearchProject:
    project = await repo.get_project_by_id(db, project_id)
    if not project:
        raise NotFoundException("研发项目", str(project_id))
    return project


async def get_projects(
    db: AsyncSession,
    stage: str | None = None,
    status: str | None = None,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[ResearchProject], int]:
    return await repo.get_projects(
        db, stage=stage, status=status, keyword=keyword, page=page, page_size=page_size
    )


async def update_project(
    db: AsyncSession,
    project_id: uuid.UUID,
    data: ResearchProjectUpdate,
) -> ResearchProject:
    project = await get_project(db, project_id)
    update_data = data.model_dump(exclude_unset=True)
    if "project_no" in update_data and update_data["project_no"] != project.project_no:
        if await repo.exists_by_project_no(db, update_data["project_no"], exclude_id=project_id):
            raise DuplicateException("项目编号", update_data["project_no"])
    return await repo.update_project(db, project, update_data)


async def delete_project(db: AsyncSession, project_id: uuid.UUID) -> None:
    project = await get_project(db, project_id)
    await repo.delete_project(db, project)
