"""Procurement ORM models live here."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from sqlalchemy import Boolean, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import BaseModel


class InvoiceRecognitionRecord(BaseModel):
    """采购发票识别结果记录表。"""

    __tablename__ = "invoice_recognition_records"
    __table_args__ = (
        Index(
            "ix_procurement_invoice_recognition_invoice_number",
            "invoice_number",
        ),
        Index(
            "ix_procurement_invoice_recognition_duplicate_key",
            "duplicate_key",
        ),
        Index(
            "ix_procurement_invoice_recognition_source_file_sha256",
            "source_file_sha256",
        ),
        Index(
            "ix_procurement_invoice_recognition_seller_name",
            "seller_name",
        ),
        Index(
            "ix_procurement_invoice_recognition_created_at",
            "created_at",
        ),
        {"schema": "procurement"},
    )

    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="上传文件名",
    )
    include_details: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        comment="是否开启明细识别",
    )
    invoice_number: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        comment="发票号码",
    )
    duplicate_key: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        comment="发票业务去重指纹",
    )
    source_file_sha256: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        comment="上传文件 SHA256",
    )
    invoice_date: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
        comment="开票日期",
    )
    seller_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="销售方名称",
    )
    total_tax_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 2),
        nullable=True,
        comment="税额合计",
    )
    total_amount_with_tax_small: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 2),
        nullable=True,
        comment="价税合计（小写）",
    )
    line_items: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default="[]",
        comment="识别到的发票明细",
    )
    raw_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
        server_default="",
        comment="PDF 文本层原文",
    )
