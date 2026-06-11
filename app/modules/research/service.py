"""Research business workflows."""

from typing import Any

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
    # Auto-generate project_no if not provided
    project_no = data.project_no
    if not project_no:
        import uuid
        project_no = f"PRJ-{str(uuid.uuid4())[:8].upper()}"
    
    if await repo.exists_by_project_no(db, project_no):
        raise DuplicateException("项目编号", project_no)
    
    project_data = data.model_dump()
    project_data["project_no"] = project_no
    return await repo.create_project(db, project_data)


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
    project_type: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[ResearchProject], int]:
    return await repo.get_projects(
        db, stage=stage, status=status, keyword=keyword, project_type=project_type,
        page=page, page_size=page_size
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


# ============ Bayesian Component Operations ============

async def create_component(db: AsyncSession, project_id: uuid.UUID, data: dict) -> Any:
    data["project_id"] = project_id
    return await repo.create_component(db, data)


async def get_components(db: AsyncSession, project_id: uuid.UUID) -> list[Any]:
    return await repo.get_components_by_project(db, project_id)


async def delete_component(db: AsyncSession, component_id: uuid.UUID) -> None:
    component = await repo.get_component_by_id(db, component_id)
    if not component:
        raise NotFoundException("参数", str(component_id))
    await repo.delete_component(db, component)


# ============ Bayesian Objective Operations ============

async def create_objective(db: AsyncSession, project_id: uuid.UUID, data: dict) -> Any:
    data["project_id"] = project_id
    return await repo.create_objective(db, data)


async def get_objectives(db: AsyncSession, project_id: uuid.UUID) -> list[Any]:
    return await repo.get_objectives_by_project(db, project_id)


async def delete_objective(db: AsyncSession, objective_id: uuid.UUID) -> None:
    objective = await repo.get_objective_by_id(db, objective_id)
    if not objective:
        raise NotFoundException("目标", str(objective_id))
    await repo.delete_objective(db, objective)


# ============ Bayesian Experiment Operations ============

async def create_experiment(db: AsyncSession, project_id: uuid.UUID, data: dict) -> Any:
    data["project_id"] = project_id
    return await repo.create_experiment(db, data)


async def get_experiments(db: AsyncSession, project_id: uuid.UUID) -> list[Any]:
    return await repo.get_experiments_by_project(db, project_id)


async def record_experiment_result(
    db: AsyncSession,
    experiment_id: uuid.UUID,
    results: dict,
) -> Any:
    experiment = await repo.get_experiment_by_id(db, experiment_id)
    if not experiment:
        raise NotFoundException("实验", str(experiment_id))
    return await repo.update_experiment_results(db, experiment, results)


# ============ Bayesian Project Operations ============

async def create_bayesian_project(db: AsyncSession, data: dict) -> Any:
    return await repo.create_bayesian_project(db, data)


async def get_bayesian_projects(
    db: AsyncSession,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Any], int]:
    return await repo.get_bayesian_projects(db, keyword=keyword, page=page, page_size=page_size)


async def get_bayesian_project(db: AsyncSession, project_id: uuid.UUID) -> Any:
    project = await repo.get_bayesian_project_by_id(db, project_id)
    if not project:
        raise NotFoundException("贝叶斯项目", str(project_id))
    return project


async def update_bayesian_project(
    db: AsyncSession,
    project_id: uuid.UUID,
    data: dict,
) -> Any:
    project = await get_bayesian_project(db, project_id)
    return await repo.update_bayesian_project(db, project, data)


async def delete_bayesian_project(db: AsyncSession, project_id: uuid.UUID) -> None:
    project = await get_bayesian_project(db, project_id)
    await repo.delete_bayesian_project(db, project)
