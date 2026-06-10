"""Research service for Bayesian optimization."""

import io
import uuid
import itertools
import pandas as pd
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, AppException
from app.modules.research import repository
from app.modules.research.models import (
    BayesianProject,
    BayesianComponent,
    BayesianObjective,
    BayesianExperiment,
    ReactionScope,
)
from app.modules.research.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ComponentCreate,
    ObjectiveCreate,
    ExperimentSuggest,
)


# ============ Project Service ============
async def create_project(db: AsyncSession, data: ProjectCreate) -> BayesianProject:
    """创建贝叶斯优化项目"""
    project = BayesianProject(
        name=data.name,
        description=data.description,
        status="draft",
    )
    project = await repository.create_project(db, project)

    # 创建组件
    for comp_data in data.components:
        component = BayesianComponent(
            project_id=project.id,
            name=comp_data.name,
            lower_bound=comp_data.lower_bound,
            upper_bound=comp_data.upper_bound,
            interval=comp_data.interval,
            unit=comp_data.unit,
            sort_order=comp_data.sort_order,
        )
        await repository.create_component(db, component)

    # 创建目标
    for obj_data in data.objectives:
        objective = BayesianObjective(
            project_id=project.id,
            name=obj_data.name,
            direction=obj_data.direction,
            weight=obj_data.weight,
        )
        await repository.create_objective(db, objective)

    return await repository.get_project(db, project.id)


async def get_project(db: AsyncSession, project_id: uuid.UUID) -> BayesianProject:
    """获取项目详情"""
    project = await repository.get_project(db, project_id)
    if not project:
        raise NotFoundException("项目")
    return project


async def get_projects(db: AsyncSession) -> list[BayesianProject]:
    """获取项目列表"""
    return await repository.get_projects(db)


async def update_project(
    db: AsyncSession, project_id: uuid.UUID, data: ProjectUpdate
) -> BayesianProject:
    """更新项目"""
    project = await repository.get_project(db, project_id)
    if not project:
        raise NotFoundException("项目")

    if data.name is not None:
        project.name = data.name
    if data.description is not None:
        project.description = data.description
    if data.status is not None:
        project.status = data.status

    return await repository.update_project(db, project)


async def delete_project(db: AsyncSession, project_id: uuid.UUID) -> None:
    """删除项目"""
    project = await repository.get_project(db, project_id)
    if not project:
        raise NotFoundException("项目")
    await repository.delete_project(db, project_id)


# ============ Component Service ============
async def add_component(
    db: AsyncSession, project_id: uuid.UUID, data: ComponentCreate
) -> BayesianComponent:
    """添加组件"""
    project = await repository.get_project(db, project_id)
    if not project:
        raise NotFoundException("项目")

    component = BayesianComponent(
        project_id=project_id,
        name=data.name,
        lower_bound=data.lower_bound,
        upper_bound=data.upper_bound,
        interval=data.interval,
        unit=data.unit,
        sort_order=data.sort_order,
    )
    return await repository.create_component(db, component)


async def get_components(db: AsyncSession, project_id: uuid.UUID) -> list[BayesianComponent]:
    """获取组件列表"""
    return await repository.get_components(db, project_id)

async def delete_component(db: AsyncSession, component_id: uuid.UUID) -> None:
    """删除组件"""
    await repository.delete_component(db, component_id)



# ============ Objective Service ============
async def add_objective(
    db: AsyncSession, project_id: uuid.UUID, data: ObjectiveCreate
) -> BayesianObjective:
    """添加目标"""
    project = await repository.get_project(db, project_id)
    if not project:
        raise NotFoundException("项目")

    objective = BayesianObjective(
        project_id=project_id,
        name=data.name,
        direction=data.direction,
        weight=data.weight,
    )
    return await repository.create_objective(db, objective)


async def get_objectives(db: AsyncSession, project_id: uuid.UUID) -> list[BayesianObjective]:
    """获取目标列表"""
    return await repository.get_objectives(db, project_id)

async def delete_objective(db: AsyncSession, objective_id: uuid.UUID) -> None:
    """删除目标"""
    await repository.delete_objective(db, objective_id)



# ============ Experiment Service ============
async def suggest_experiments(
    db: AsyncSession, data: ExperimentSuggest
) -> list[BayesianExperiment]:
    """推荐下一批实验（简化版贝叶斯优化）"""
    project = await repository.get_project(db, data.project_id)
    if not project:
        raise NotFoundException("项目")

    components = await repository.get_components(db, data.project_id)
    if not components:
        raise AppException("请先添加反应组件")

    # 获取已有实验
    existing = await repository.get_experiments(db, data.project_id)
    existing_count = len(existing)

    # 生成推荐实验点
    suggestions = _generate_suggestions(components, existing, data.num_experiments)

    # 保存推荐结果
    experiments = []
    for i, params in enumerate(suggestions):
        experiment = BayesianExperiment(
            project_id=data.project_id,
            batch_number=existing_count + i + 1,
            parameters=params,
            is_suggested=True,
            status="pending",
        )
        experiment = await repository.create_experiment(db, experiment)
        experiments.append(experiment)

    # 更新项目状态
    project.status = "running"
    await repository.update_project(db, project)

    return experiments


def _generate_suggestions(
    components: list[BayesianComponent],
    existing: list[BayesianExperiment],
    num_suggestions: int,
) -> list[dict]:
    """生成实验建议（简化版：使用拉丁超立方采样）"""
    # 如果已有实验数据，可以基于此优化（这里简化处理）
    # 实际应该使用 BoTorch 进行真正的贝叶斯优化

    suggestions = []

    if len(existing) == 0:
        # 第一批实验：使用拉丁超立方采样
        for i in range(num_suggestions):
            params = {}
            for comp in components:
                # 均匀分布采样
                if comp.interval:
                    num_points = int((comp.upper_bound - comp.lower_bound) / comp.interval) + 1
                    values = np.linspace(comp.lower_bound, comp.upper_bound, num_points)
                    value = values[i % len(values)]
                else:
                    value = comp.lower_bound + (comp.upper_bound - comp.lower_bound) * (i / num_suggestions)
                params[comp.name] = round(value, 4)
            suggestions.append(params)
    else:
        # 后续实验：基于已有数据探索未覆盖区域
        for i in range(num_suggestions):
            params = {}
            for comp in components:
                # 添加一些随机性来探索
                np.random.seed(len(existing) + i)
                value = np.random.uniform(comp.lower_bound, comp.upper_bound)
                if comp.interval:
                    value = round(value / comp.interval) * comp.interval
                params[comp.name] = round(value, 4)
            suggestions.append(params)

    return suggestions


async def record_experiment_result(
    db: AsyncSession, experiment_id: uuid.UUID, results: dict, status: str = "completed"
) -> BayesianExperiment:
    """记录实验结果"""
    result = await db.get(BayesianExperiment, experiment_id)
    if not result:
        raise NotFoundException("实验记录")

    result.results = results
    result.status = status
    return await repository.update_experiment(db, result)


async def get_experiments(
    db: AsyncSession, project_id: uuid.UUID
) -> list[BayesianExperiment]:
    """获取实验列表"""
    return await repository.get_experiments(db, project_id)


# ============ Reaction Scope Service ============
async def generate_reaction_scope(
    db: AsyncSession, project_id: uuid.UUID, name: str
) -> ReactionScope:
    """生成反应范围"""
    project = await repository.get_project(db, project_id)
    if not project:
        raise NotFoundException("项目")

    components = await repository.get_components(db, project_id)
    if not components:
        raise AppException("请先添加反应组件")

    # 计算所有组合
    scope_data = _calculate_scope(components)
    total = scope_data["total_combinations"]

    scope = ReactionScope(
        project_id=project_id,
        name=name,
        scope_data=scope_data,
        total_combinations=total,
    )
    return await repository.create_reaction_scope(db, scope)


def _calculate_scope(components: list[BayesianComponent]) -> dict:
    """计算反应范围"""
    ranges = {}
    total = 1

    for comp in components:
        if comp.interval:
            num_points = int((comp.upper_bound - comp.lower_bound) / comp.interval) + 1
            values = [
                round(comp.lower_bound + i * comp.interval, 4)
                for i in range(num_points)
            ]
        else:
            # 默认 10 个点
            values = np.linspace(comp.lower_bound, comp.upper_bound, 10).tolist()
            values = [round(v, 4) for v in values]

        ranges[comp.name] = {
            "values": values,
            "unit": comp.unit,
        }
        total *= len(values)

    return {
        "components": ranges,
        "total_combinations": total,
    }


async def get_reaction_scopes(
    db: AsyncSession, project_id: uuid.UUID
) -> list[ReactionScope]:
    """获取反应范围列表"""
    return await repository.get_reaction_scopes(db, project_id)


# ============ CSV Import/Export Service ============
async def import_csv(db: AsyncSession, project_id: uuid.UUID, file_content: bytes) -> dict:
    """导入 CSV 实验数据"""
    project = await repository.get_project(db, project_id)
    if not project:
        raise NotFoundException("项目")

    try:
        df = pd.read_csv(io.BytesIO(file_content))
    except Exception as e:
        raise AppException(f"CSV 文件解析失败: {str(e)}")

    # 获取组件列表
    components = await repository.get_components(db, project_id)
    comp_names = [c.name for c in components]

    # 验证列
    missing_cols = [c for c in comp_names if c not in df.columns]
    if missing_cols:
        raise AppException(f"CSV 缺少组件列: {', '.join(missing_cols)}")

    # 导入数据
    existing = await repository.get_experiments(db, project_id)
    batch_start = len(existing) + 1

    imported = 0
    for idx, row in df.iterrows():
        params = {name: float(row[name]) for name in comp_names}
        results = {}

        # 如果有结果列
        for col in df.columns:
            if col not in comp_names and col not in ["batch", "batch_number"]:
                try:
                    results[col] = float(row[col])
                except (ValueError, TypeError):
                    results[col] = row[col]

        experiment = BayesianExperiment(
            project_id=project_id,
            batch_number=batch_start + idx,
            parameters=params,
            results=results if results else None,
            is_suggested=False,
            status="completed" if results else "pending",
        )
        await repository.create_experiment(db, experiment)
        imported += 1

    return {
        "success": True,
        "message": f"成功导入 {imported} 条实验数据",
        "rows_imported": imported,
    }


async def export_csv(db: AsyncSession, project_id: uuid.UUID) -> bytes:
    """导出实验数据为 CSV"""
    project = await repository.get_project(db, project_id)
    if not project:
        raise NotFoundException("项目")

    experiments = await repository.get_experiments(db, project_id)
    components = await repository.get_components(db, project_id)

    if not experiments:
        raise AppException("没有实验数据可导出")

    # 构建 DataFrame
    rows = []
    for exp in experiments:
        row = {"batch_number": exp.batch_number}
        row.update(exp.parameters)
        if exp.results:
            row.update(exp.results)
        row["status"] = exp.status
        rows.append(row)

    df = pd.DataFrame(rows)
    output = io.BytesIO()
    df.to_csv(output, index=False)
    return output.getvalue()
