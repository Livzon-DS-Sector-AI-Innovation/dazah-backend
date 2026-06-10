"""Quality ORM models live here."""

from datetime import date, datetime
from uuid import UUID

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import BaseModel


class LabelVerification(BaseModel):
    """标签复核记录表"""

    __tablename__ = "label_verifications"
    __table_args__ = (
        Index("ix_label_verifications_batch_number", "batch_number"),
        Index("ix_label_verifications_production_date", "production_date"),
        Index("ix_label_verifications_verification_date", "verification_date"),
        Index("ix_label_verifications_result_status", "result_status"),
        {"schema": "production"},
    )

    # 基础信息
    batch_number: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="批号，如 QS32603006"
    )
    product_name: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="产品名称"
    )
    production_date: Mapped[date] = mapped_column(
        Date, nullable=False, comment="生产日期"
    )
    expiry_date: Mapped[date] = mapped_column(
        Date, nullable=False, comment="有效期至"
    )

    # 桶数与重量信息
    total_barrels: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="总桶数"
    )
    standard_barrels: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="整桶数"
    )
    remainder_barrel: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="零头桶数（0或1）"
    )
    standard_weight: Mapped[float] = mapped_column(
        Float, nullable=False, comment="整桶重量（kg）"
    )
    remainder_weight: Mapped[float] = mapped_column(
        Float, nullable=False, comment="零头重量（kg）"
    )
    total_weight: Mapped[float] = mapped_column(
        Float, nullable=False, comment="总重量（kg）"
    )

    # 8项结论状态（True=一致，False=不一致）
    check_batch_number: Mapped[bool] = mapped_column(
        Boolean, nullable=False, comment="批号对比结果"
    )
    check_production_date: Mapped[bool] = mapped_column(
        Boolean, nullable=False, comment="生产日期对比结果"
    )
    check_expiry_date: Mapped[bool] = mapped_column(
        Boolean, nullable=False, comment="有效期至对比结果"
    )
    check_standard_barrels: Mapped[bool] = mapped_column(
        Boolean, nullable=False, comment="整桶信息对比结果"
    )
    check_remainder_barrel: Mapped[bool] = mapped_column(
        Boolean, nullable=False, comment="零头信息对比结果"
    )
    check_total_weight: Mapped[bool] = mapped_column(
        Boolean, nullable=False, comment="总重量对比结果"
    )
    check_all_barrels_identified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, comment="是否识别到每一桶"
    )
    check_exception_handled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, comment="异常处理结果"
    )

    # 总体结论
    result_status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="全部一致",
        server_default="全部一致",
        comment="总体结论：全部一致/存在差异",
    )
    result_summary: Mapped[str] = mapped_column(
        Text, nullable=False, comment="结论摘要，如 ✅✅✅ 全部一致"
    )

    # 视频来源信息
    video_file_key: Mapped[str] = mapped_column(
        String(256), nullable=False, comment="视频文件 key（用于去重）"
    )
    video_file_name: Mapped[str] = mapped_column(
        String(256), nullable=True, comment="视频文件名"
    )
    video_frame_count: Mapped[int] = mapped_column(
        Integer, nullable=True, comment="提取帧数"
    )
    video_fps: Mapped[float] = mapped_column(
        Float, nullable=True, comment="帧率（2.0 或 3.0）"
    )

    # 复核时间
    verification_date: Mapped[date] = mapped_column(
        Date, nullable=False, comment="复核日期"
    )
    verification_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, comment="复核时间"
    )

    # 备注
    remarks: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="备注"
    )
