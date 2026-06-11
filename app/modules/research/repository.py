"""Research database queries."""

import uuid
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.research.models import ResearchProject


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


async def exists_by_project_no(
    db: AsyncSession,
    project_no: str,
    exclude_id: uuid.UUID | None = None,
) -> bool:
    query = select(ResearchProject.id).where(
        ResearchProject.project_no == project_no,
        ResearchProject.is_deleted == False,  # noqa: E712
    )
    if exclude_id:
        query = query.where(ResearchProject.id != exclude_id)
    result = await db.execute(query.limit(1))
    return result.scalar_one_or_none() is not None


async def create_project(db: AsyncSession, data: dict[str, Any]) -> ResearchProject:
    project = ResearchProject(**data)
    db.add(project)
    await db.flush()
    return project


async def get_project_by_id(
    db: AsyncSession, project_id: uuid.UUID
) -> ResearchProject | None:
    result = await db.execute(
        select(ResearchProject).where(
            ResearchProject.id == project_id,
            ResearchProject.is_deleted == False,  # noqa: E712
        )
    )
    return result.scalar_one_or_none()


async def get_projects(
    db: AsyncSession,
    stage: str | None = None,
    status: str | None = None,
    keyword: str | None = None,
    project_type: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[ResearchProject], int]:
    query = select(ResearchProject).where(
        ResearchProject.is_deleted == False,  # noqa: E712
    )
    count_query = select(func.count()).select_from(ResearchProject).where(
        ResearchProject.is_deleted == False,  # noqa: E712
    )

    if stage:
        query = query.where(ResearchProject.stage == stage)
        count_query = count_query.where(ResearchProject.stage == stage)
    if status:
        query = query.where(ResearchProject.status == status)
        count_query = count_query.where(ResearchProject.status == status)
    if keyword:
        pattern = f"%{_escape_like(keyword)}%"
        like_filter = or_(
            ResearchProject.project_no.ilike(pattern),
            ResearchProject.name.ilike(pattern),
        )
        query = query.where(like_filter)
        count_query = count_query.where(like_filter)
    if project_type is not None:
        if project_type == "":
            query = query.where(ResearchProject.project_type == None)
            count_query = count_query.where(ResearchProject.project_type == None)
        else:
            query = query.where(ResearchProject.project_type == project_type)
            count_query = count_query.where(ResearchProject.project_type == project_type)

    total = (await db.execute(count_query)).scalar_one()

    query = query.order_by(ResearchProject.updated_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size)
    result = await db.execute(query)
    return result.scalars().all(), total


async def update_project(
    db: AsyncSession,
    project: ResearchProject,
    data: dict[str, Any],
) -> ResearchProject:
    for key, value in data.items():
        setattr(project, key, value)
    await db.flush()
    return project


async def delete_project(db: AsyncSession, project: ResearchProject) -> None:
    project.is_deleted = True
    await db.flush()


# ============ Bayesian Component Operations ============

async def create_component(db: AsyncSession, data: dict[str, Any]) -> Any:
    from app.modules.research.models import BayesianComponent
    component = BayesianComponent(**data)
    db.add(component)
    await db.flush()
    return component


async def get_components_by_project(
    db: AsyncSession, project_id: uuid.UUID
) -> list[Any]:
    from app.modules.research.models import BayesianComponent
    result = await db.execute(
        select(BayesianComponent).where(
            BayesianComponent.project_id == project_id,
            BayesianComponent.is_deleted == False,  # noqa: E712
        )
    )
    return result.scalars().all()


async def get_component_by_id(
    db: AsyncSession, component_id: uuid.UUID
) -> Any | None:
    from app.modules.research.models import BayesianComponent
    result = await db.execute(
        select(BayesianComponent).where(
            BayesianComponent.id == component_id,
            BayesianComponent.is_deleted == False,  # noqa: E712
        )
    )
    return result.scalar_one_or_none()


async def delete_component(db: AsyncSession, component: Any) -> None:
    component.is_deleted = True
    await db.flush()


# ============ Bayesian Objective Operations ============

async def create_objective(db: AsyncSession, data: dict[str, Any]) -> Any:
    from app.modules.research.models import BayesianObjective
    objective = BayesianObjective(**data)
    db.add(objective)
    await db.flush()
    return objective


async def get_objectives_by_project(
    db: AsyncSession, project_id: uuid.UUID
) -> list[Any]:
    from app.modules.research.models import BayesianObjective
    result = await db.execute(
        select(BayesianObjective).where(
            BayesianObjective.project_id == project_id,
            BayesianObjective.is_deleted == False,  # noqa: E712
        )
    )
    return result.scalars().all()


async def get_objective_by_id(
    db: AsyncSession, objective_id: uuid.UUID
) -> Any | None:
    from app.modules.research.models import BayesianObjective
    result = await db.execute(
        select(BayesianObjective).where(
            BayesianObjective.id == objective_id,
            BayesianObjective.is_deleted == False,  # noqa: E712
        )
    )
    return result.scalar_one_or_none()


async def delete_objective(db: AsyncSession, objective: Any) -> None:
    objective.is_deleted = True
    await db.flush()


# ============ Bayesian Experiment Operations ============

async def create_experiment(db: AsyncSession, data: dict[str, Any]) -> Any:
    from app.modules.research.models import BayesianExperiment
    experiment = BayesianExperiment(**data)
    db.add(experiment)
    await db.flush()
    return experiment


async def get_experiments_by_project(
    db: AsyncSession, project_id: uuid.UUID
) -> list[Any]:
    from app.modules.research.models import BayesianExperiment
    result = await db.execute(
        select(BayesianExperiment).where(
            BayesianExperiment.project_id == project_id,
            BayesianExperiment.is_deleted == False,  # noqa: E712
        ).order_by(BayesianExperiment.batch_number.desc(), BayesianExperiment.created_at.asc())
    )
    return result.scalars().all()


async def get_experiment_by_id(
    db: AsyncSession, experiment_id: uuid.UUID
) -> Any | None:
    from app.modules.research.models import BayesianExperiment
    result = await db.execute(
        select(BayesianExperiment).where(
            BayesianExperiment.id == experiment_id,
            BayesianExperiment.is_deleted == False,  # noqa: E712
        )
    )
    return result.scalar_one_or_none()


async def update_experiment_results(
    db: AsyncSession,
    experiment: Any,
    results: dict[str, Any],
) -> Any:
    experiment.results = results
    experiment.status = "completed"
    await db.flush()
    return experiment


# ============ Bayesian Project Operations ============

async def create_bayesian_project(db: AsyncSession, data: dict[str, Any]) -> Any:
    from app.modules.research.models import BayesianProject
    project = BayesianProject(**data)
    db.add(project)
    await db.flush()
    return project


async def get_bayesian_projects(
    db: AsyncSession,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Any], int]:
    from app.modules.research.models import BayesianProject
    query = select(BayesianProject).where(
        BayesianProject.is_deleted == False,  # noqa: E712
    )
    count_query = select(func.count()).select_from(BayesianProject).where(
        BayesianProject.is_deleted == False,  # noqa: E712
    )
    
    if keyword:
        pattern = f"%{_escape_like(keyword)}%"
        query = query.where(BayesianProject.name.ilike(pattern))
        count_query = count_query.where(BayesianProject.name.ilike(pattern))
    
    total = (await db.execute(count_query)).scalar_one()
    
    query = query.order_by(BayesianProject.updated_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size)
    result = await db.execute(query)
    return result.scalars().all(), total


async def get_bayesian_project_by_id(
    db: AsyncSession, project_id: uuid.UUID
) -> Any | None:
    from app.modules.research.models import BayesianProject
    result = await db.execute(
        select(BayesianProject).where(
            BayesianProject.id == project_id,
            BayesianProject.is_deleted == False,  # noqa: E712
        )
    )
    return result.scalar_one_or_none()


async def update_bayesian_project(
    db: AsyncSession,
    project: Any,
    data: dict[str, Any],
) -> Any:
    for key, value in data.items():
        setattr(project, key, value)
    await db.flush()
    return project


async def delete_bayesian_project(db: AsyncSession, project: Any) -> None:
    project.is_deleted = True
    await db.flush()
