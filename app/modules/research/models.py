"""Research ORM models."""

import uuid
from datetime import date

from sqlalchemy import CheckConstraint, Date, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import BaseModel


class ResearchProject(BaseModel):
    """研发项目主表"""

    __tablename__ = "research_projects"
    __table_args__ = (
        CheckConstraint(
            "stage IN ('立项', '研发中试', '验证', '注册', '商业化')",
            name="ck_research_projects_stage",
        ),
        CheckConstraint(
            "status IN ('进行中', '已暂停', '已完成', '已终止')",
            name="ck_research_projects_status",
        ),
        {"schema": "research"},
    )

    project_no: Mapped[str] = mapped_column(
        String(50), comment="项目编号"
    )
    name: Mapped[str] = mapped_column(
        String(200), comment="项目名称"
    )
    project_type: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="项目类型"
    )
    stage: Mapped[str] = mapped_column(
        String(20),
        default="立项",
        comment="项目阶段：立项/研发中试/验证/注册/商业化",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="进行中",
        comment="项目状态：进行中/已暂停/已完成/已终止",
    )
    leader: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="项目负责人"
    )
    start_date: Mapped[date | None] = mapped_column(
        Date, nullable=True, comment="开始日期"
    )
    end_date: Mapped[date | None] = mapped_column(
        Date, nullable=True, comment="结束日期"
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="项目描述"
    )


class BayesianProject(BaseModel):
    """贝叶斯优化项目"""

    __tablename__ = "bayesian_projects"
    __table_args__ = {"schema": "research"}

    name: Mapped[str] = mapped_column(
        String(200), comment="项目名称"
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="项目描述"
    )
    status: Mapped[str] = mapped_column(
        String(50), default="draft", comment="项目状态: draft, running, completed, failed"
    )


class ICHAnalysisRecord(BaseModel):
    """ICH Q3C/Q3D 杂质识别分析记录"""

    __tablename__ = "ich_analysis_records"
    __table_args__ = {"schema": "research"}

    filename: Mapped[str] = mapped_column(
        String(500), comment="上传的文件名"
    )
    route: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="给药途径: oral/parenteral/inhalation/cutaneous (deprecated)"
    )
    q3c_result: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, comment="Q3C 溶剂残留分析结果"
    )
    q3d_result: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, comment="Q3D 元素杂质分析结果"
    )
    llm_used: Mapped[bool] = mapped_column(
        default=False, comment="是否使用 LLM 增强识别"
    )
    notes: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="备注"
    )


class BayesianComponent(BaseModel):
    """贝叶斯优化参数"""

    __tablename__ = "bayesian_components"
    __table_args__ = {"schema": "research"}

    project_id: Mapped[uuid.UUID] = mapped_column(
        comment="关联项目 ID"
    )
    name: Mapped[str] = mapped_column(
        String(200), comment="参数名称"
    )
    component_type: Mapped[str] = mapped_column(
        String(20), comment="参数类型: numerical 或 categorical"
    )
    lower_bound: Mapped[float | None] = mapped_column(
        nullable=True, comment="数值型下限"
    )
    upper_bound: Mapped[float | None] = mapped_column(
        nullable=True, comment="数值型上限"
    )
    data_points: Mapped[int | None] = mapped_column(
        nullable=True, comment="数值型取值数量"
    )
    categorical_values: Mapped[list | None] = mapped_column(
        JSON, nullable=True, comment="类别型取值列表"
    )


class BayesianObjective(BaseModel):
    """贝叶斯优化目标"""

    __tablename__ = "bayesian_objectives"
    __table_args__ = {"schema": "research"}

    project_id: Mapped[uuid.UUID] = mapped_column(
        comment="关联项目 ID"
    )
    name: Mapped[str] = mapped_column(
        String(200), comment="目标名称"
    )
    direction: Mapped[str] = mapped_column(
        String(20), comment="优化方向: maximize 或 minimize"
    )
    threshold: Mapped[float | None] = mapped_column(
        nullable=True, comment="阈值（可选）"
    )


class BayesianExperiment(BaseModel):
    """贝叶斯优化实验"""

    __tablename__ = "bayesian_experiments"
    __table_args__ = {"schema": "research"}

    project_id: Mapped[uuid.UUID] = mapped_column(
        comment="关联项目 ID"
    )
    batch_number: Mapped[int] = mapped_column(
        comment="批次号"
    )
    parameters: Mapped[dict] = mapped_column(
        JSON, comment="参数配置"
    )
    results: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, comment="实验结果"
    )
    is_suggested: Mapped[bool] = mapped_column(
        default=True, comment="是否为推荐实验"
    )
    status: Mapped[str] = mapped_column(
        String(50), comment="状态: pending, running, completed, failed"
    )
