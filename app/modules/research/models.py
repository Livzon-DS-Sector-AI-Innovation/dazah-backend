"""Research ORM models."""

import uuid
from datetime import date

from sqlalchemy import CheckConstraint, Date, String, Text
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

    # 关联的参数
    components: Mapped[list["BayesianComponent"]] = relationship(
        primaryjoin="BayesianProject.id == foreign(BayesianComponent.project_id)",
        cascade="all, delete-orphan",
        viewonly=False
    )
    # 关联的目标
    objectives: Mapped[list["BayesianObjective"]] = relationship(
        primaryjoin="BayesianProject.id == foreign(BayesianObjective.project_id)",
        cascade="all, delete-orphan",
        viewonly=False
    )
    # 关联的实验数据
    experiments: Mapped[list["BayesianExperiment"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
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
