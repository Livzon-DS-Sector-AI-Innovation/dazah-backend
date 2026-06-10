"""Research repository for Bayesian optimization."""

import uuid
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.research.models import (
    BayesianProject,
    BayesianComponent,
    BayesianObjective,
    BayesianExperiment,
    ReactionScope,
)


# ============ Project Repository ============
async def create_project(db: AsyncSession, project: BayesianProject) -> BayesianProject:
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


async def get_project(db: AsyncSession, project_id: uuid.UUID) -> BayesianProject | None:
    result = await db.execute(
        select(BayesianProject)
        .options(selectinload(BayesianProject.components), selectinload(BayesianProject.objectives))
        .where(BayesianProject.id == project_id, BayesianProject.is_deleted == False)
    )
    return result.scalar_one_or_none()


async def get_projects(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[BayesianProject]:
    result = await db.execute(
        select(BayesianProject)
        .where(BayesianProject.is_deleted == False)
        .offset(skip)
        .limit(limit)
        .order_by(BayesianProject.created_at.desc())
    )
    return list(result.scalars().all())


async def update_project(db: AsyncSession, project: BayesianProject) -> BayesianProject:
    await db.commit()
    await db.refresh(project)
    return project


async def delete_project(db: AsyncSession, project_id: uuid.UUID) -> None:
    result = await db.execute(
        select(BayesianProject).where(BayesianProject.id == project_id)
    )
    project = result.scalar_one_or_none()
    if project:
        project.is_deleted = True
        await db.commit()


# ============ Component Repository ============
async def create_component(db: AsyncSession, component: BayesianComponent) -> BayesianComponent:
    db.add(component)
    await db.commit()
    await db.refresh(component)
    return component


async def get_components(db: AsyncSession, project_id: uuid.UUID) -> list[BayesianComponent]:
    result = await db.execute(
        select(BayesianComponent)
        .where(BayesianComponent.project_id == project_id, BayesianComponent.is_deleted == False)
        .order_by(BayesianComponent.sort_order)
    )
    return list(result.scalars().all())




async def delete_component(db: AsyncSession, component_id: uuid.UUID) -> None:
    result = await db.execute(
        select(BayesianComponent).where(BayesianComponent.id == component_id)
    )
    component = result.scalar_one_or_none()
    if component:
        component.is_deleted = True
        await db.commit()


async def delete_components_by_project(db: AsyncSession, project_id: uuid.UUID) -> None:
    await db.execute(
        delete(BayesianComponent).where(BayesianComponent.project_id == project_id)
    )
    await db.commit()


# ============ Objective Repository ============
async def create_objective(db: AsyncSession, objective: BayesianObjective) -> BayesianObjective:
    db.add(objective)
    await db.commit()
    await db.refresh(objective)
    return objective


async def get_objectives(db: AsyncSession, project_id: uuid.UUID) -> list[BayesianObjective]:
    result = await db.execute(
        select(BayesianObjective)
        .where(BayesianObjective.project_id == project_id, BayesianObjective.is_deleted == False)
    )
    return list(result.scalars().all())




async def delete_objective(db: AsyncSession, objective_id: uuid.UUID) -> None:
    result = await db.execute(
        select(BayesianObjective).where(BayesianObjective.id == objective_id)
    )
    objective = result.scalar_one_or_none()
    if objective:
        objective.is_deleted = True
        await db.commit()


async def delete_objectives_by_project(db: AsyncSession, project_id: uuid.UUID) -> None:
    await db.execute(
        delete(BayesianObjective).where(BayesianObjective.project_id == project_id)
    )
    await db.commit()


# ============ Experiment Repository ============
async def create_experiment(db: AsyncSession, experiment: BayesianExperiment) -> BayesianExperiment:
    db.add(experiment)
    await db.commit()
    await db.refresh(experiment)
    return experiment


async def get_experiments(
    db: AsyncSession, project_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[BayesianExperiment]:
    result = await db.execute(
        select(BayesianExperiment)
        .where(BayesianExperiment.project_id == project_id, BayesianExperiment.is_deleted == False)
        .offset(skip)
        .limit(limit)
        .order_by(BayesianExperiment.batch_number)
    )
    return list(result.scalars().all())


async def update_experiment(db: AsyncSession, experiment: BayesianExperiment) -> BayesianExperiment:
    await db.commit()
    await db.refresh(experiment)
    return experiment


# ============ Reaction Scope Repository ============
async def create_reaction_scope(db: AsyncSession, scope: ReactionScope) -> ReactionScope:
    db.add(scope)
    await db.commit()
    await db.refresh(scope)
    return scope


async def get_reaction_scopes(db: AsyncSession, project_id: uuid.UUID) -> list[ReactionScope]:
    result = await db.execute(
        select(ReactionScope)
        .where(ReactionScope.project_id == project_id, ReactionScope.is_deleted == False)
        .order_by(ReactionScope.created_at.desc())
    )
    return list(result.scalars().all())
