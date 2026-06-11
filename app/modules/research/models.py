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
