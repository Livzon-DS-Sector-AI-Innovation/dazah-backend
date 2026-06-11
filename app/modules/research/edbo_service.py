"""EDBO Plus integration service for Bayesian optimization."""

import uuid
import tempfile
import os
from pathlib import Path
import numpy as np
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.research import service


async def suggest_experiments(
    db: AsyncSession,
    project_id: uuid.UUID,
    batch_size: int = 5,
) -> list[dict]:
    """
    Run EDBO optimization and suggest experiments.
    
    1. Load components from database
    2. Convert to EDBO format (generate discrete values)
    3. Generate reaction scope (cartesian product)
    4. Load existing completed experiments as training data
    5. Run EDBO optimization
    6. Save suggested experiments to database
    """
    # Load components and objectives
    components = await service.get_components(db, project_id)
    objectives = await service.get_objectives(db, project_id)
    
    if not components:
        raise ValueError("项目没有定义参数")
    if not objectives:
        raise ValueError("项目没有定义优化目标")
    
    # Convert components to EDBO format
    edbo_components = {}
    for comp in components:
        if comp.component_type == "numerical":
            # Generate evenly-spaced values
            values = np.linspace(
                comp.lower_bound,
                comp.upper_bound,
                comp.data_points
            ).tolist()
            edbo_components[comp.name] = values
        else:  # categorical
            edbo_components[comp.name] = comp.categorical_values
    
    # Load existing completed experiments
    experiments = await service.get_experiments(db, project_id)
    completed_experiments = [
        exp for exp in experiments 
        if exp.status == "completed" and exp.results
    ]
    
    # Determine current iteration
    iteration = 1
    if experiments:
        iteration = max(exp.iteration for exp in experiments) + 1
    
    # Generate reaction scope and run EDBO
    with tempfile.TemporaryDirectory() as tmpdir:
        scope_file = Path(tmpdir) / "reaction.csv"
        output_file = Path(tmpdir) / "output.csv"
        
        # Generate scope
        from edbo.plus.optimizer_botorch import EDBOplus
        scope_df = EDBOplus.generate_reaction_scope(
            components=edbo_components,
            directory=str(tmpdir),
            filename="reaction.csv",
            check_overwrite=False
        )
        
        # If we have training data, merge with scope
        if completed_experiments:
            training_df = pd.DataFrame([
                {**exp.components, **exp.results}
                for exp in completed_experiments
            ])
            # Append training data to scope
            scope_df = pd.concat([scope_df, training_df], ignore_index=True)
            scope_df.to_csv(scope_file, index=False)
        
        # Prepare objective names and modes
        objective_names = [obj.name for obj in objectives]
        objective_modes = [
            "max" if obj.direction == "maximize" else "min"
            for obj in objectives
        ]
        
        # Run EDBO optimization
        try:
            result_df = EDBOplus().run(
                objectives=objective_names,
                objective_mode=objective_modes,
                directory=str(tmpdir),
                filename="reaction.csv",
                batch=batch_size,
                columns_features="all",
                init_sampling_method="cvt",
            )
        except Exception as e:
            # If EDBO fails (e.g., no training data), return initial samples
            if completed_experiments:
                # Re-run without training data
                result_df = EDBOplus().run(
                    objectives=objective_names,
                    objective_mode=objective_modes,
                    directory=str(tmpdir),
                    filename="reaction.csv",
                    batch=batch_size,
                    columns_features="all",
                    init_sampling_method="cvt",
                )
            else:
                # Use scope directly for initial batch
                result_df = scope_df.head(batch_size)
                result_df["priority"] = list(range(batch_size))
        
        # Save suggested experiments to database
        suggested = []
        component_names = [comp.name for comp in components]
        
        for idx, row in result_df.head(batch_size).iterrows():
            parameters_dict = {name: row[name] for name in component_names}
            
            experiment = await service.create_experiment(
                db,
                project_id,
                {
                    "batch_number": iteration,
                    "parameters": parameters_dict,
                    "status": "pending",
                    "is_suggested": True,
                }
            )
            
            suggested.append({
                "id": str(experiment.id),
                "batch_number": experiment.batch_number,
                "parameters": experiment.parameters,
                "status": experiment.status,
                "is_suggested": experiment.is_suggested,
            })
        
        return suggested
