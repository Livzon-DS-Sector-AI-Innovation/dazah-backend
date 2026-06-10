"""Research ORM models for Bayesian optimization."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base_model import BaseModel


class BayesianProject(BaseModel):
    """贝叶斯优化项目"""

    __tablename__ = "bayesian_projects"
    __table_args__ = {"schema": "research"}

    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="项目名称")
    description: Mapped[str | None] = mapped_column(Text, comment="项目描述")
    status: Mapped[str] = mapped_column(
        String(50), default="draft", comment="状态: draft/running/completed/failed"
    )

    # 关联的实验数据
    experiments: Mapped[list["BayesianExperiment"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class BayesianComponent(BaseModel):
    """反应组件定义"""

    __tablename__ = "bayesian_components"
    __table_args__ = {"schema": "research"}

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("research.bayesian_projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="组件名称")
    lower_bound: Mapped[float] = mapped_column(Float, nullable=False, comment="下限")
    upper_bound: Mapped[float] = mapped_column(Float, nullable=False, comment="上限")
    interval: Mapped[float | None] = mapped_column(Float, comment="间隔")
    unit: Mapped[str | None] = mapped_column(String(50), comment="单位")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, comment="排序")


class BayesianObjective(BaseModel):
    """优化目标定义"""

    __tablename__ = "bayesian_objectives"
    __table_args__ = {"schema": "research"}

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("research.bayesian_projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="目标名称")
    direction: Mapped[str] = mapped_column(
        String(20), default="maximize", comment="优化方向: maximize/minimize"
    )
    weight: Mapped[float] = mapped_column(Float, default=1.0, comment="权重")


class BayesianExperiment(BaseModel):
    """实验记录"""

    __tablename__ = "bayesian_experiments"
    __table_args__ = {"schema": "research"}

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("research.bayesian_projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    project: Mapped["BayesianProject"] = relationship(back_populates="experiments")

    batch_number: Mapped[int] = mapped_column(Integer, nullable=False, comment="批次号")
    parameters: Mapped[dict] = mapped_column(JSONB, nullable=False, comment="参数组合")
    results: Mapped[dict | None] = mapped_column(JSONB, comment="实验结果")
    is_suggested: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否推荐")
    status: Mapped[str] = mapped_column(
        String(50), default="pending", comment="状态: pending/completed/failed"
    )


class ReactionScope(BaseModel):
    """反应范围定义"""

    __tablename__ = "reaction_scopes"
    __table_args__ = {"schema": "research"}

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("research.bayesian_projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="范围名称")
    scope_data: Mapped[dict] = mapped_column(JSONB, nullable=False, comment="范围数据")
    total_combinations: Mapped[int] = mapped_column(Integer, default=0, comment="总组合数")
