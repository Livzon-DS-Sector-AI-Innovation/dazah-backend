"""Quality management ORM models."""

import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import BaseModel


class Deviation(BaseModel):
    __tablename__ = "deviations"
    __table_args__ = {"schema": "quality"}

    deviation_code: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    department: Mapped[str | None] = mapped_column(String(255), nullable=True)
    discovery_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    discovery_time: Mapped[str | None] = mapped_column(Text, nullable=True)
    discovery_location: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft", server_default="draft")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    immediate_actions: Mapped[str | None] = mapped_column(Text, nullable=True)
    reporter_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("identity.users.id"), nullable=True)
    handler: Mapped[str | None] = mapped_column(String(255), nullable=True)
    discoverer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    root_cause_category: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ai_analysis: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    investigation_records: Mapped[list | None] = mapped_column(JSON, nullable=True)
    review_opinions: Mapped[list | None] = mapped_column(JSON, nullable=True)
    attachments: Mapped[list | None] = mapped_column(ARRAY(Text), nullable=True)
    final_code: Mapped[str | None] = mapped_column(String(255), nullable=True)
    returned_step: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    needs_cross_dept_review: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=True, server_default="true")
    cross_dept_reviewers: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    affected_items: Mapped[str | None] = mapped_column(Text, nullable=True)
    batch_number: Mapped[str | None] = mapped_column(Text, nullable=True)
    report_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    report_versions: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)


class CAPA(BaseModel):
    __tablename__ = "capas"
    __table_args__ = {"schema": "quality"}

    capa_code: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft", server_default="draft")
    deviation_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("quality.deviations.id"), nullable=True)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_code: Mapped[str | None] = mapped_column(String(255), nullable=True)
    category: Mapped[str | None] = mapped_column(String(255), nullable=True)
    root_cause_category: Mapped[str | None] = mapped_column(String(255), nullable=True)
    non_conformity_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    root_cause_analysis: Mapped[str | None] = mapped_column(Text, nullable=True)
    capa_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    capa_items: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    executors: Mapped[list | None] = mapped_column(ARRAY(Text), nullable=True)
    expected_completion_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    qa_reviewer_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("identity.users.id"), nullable=True)
    qa_review_opinion: Mapped[str | None] = mapped_column(Text, nullable=True)
    qa_review_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    q_head_approver_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("identity.users.id"), nullable=True)
    q_head_approval_opinion: Mapped[str | None] = mapped_column(Text, nullable=True)
    q_head_approval_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    execution_status: Mapped[str | None] = mapped_column(Text, nullable=True)
    execution_tracks: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    dept_head_confirmations: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    evaluation_result: Mapped[str | None] = mapped_column(Text, nullable=True)
    evaluation_target: Mapped[str | None] = mapped_column(Text, nullable=True)
    evaluation_deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    evaluation_confirmer_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("identity.users.id"), nullable=True)
    evaluation_confirm_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closure_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closure_remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    final_code: Mapped[str | None] = mapped_column(String(255), nullable=True)
    report_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    report_versions: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    returned_step: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reporter: Mapped[str | None] = mapped_column(String(255), nullable=True)
    qa_confirmer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    qa_confirm_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    root_cause_attachments: Mapped[list | None] = mapped_column(ARRAY(Text), nullable=True)
    reason_category: Mapped[str | None] = mapped_column(String(255), nullable=True)


class DepartmentContact(BaseModel):
    __tablename__ = "department_contacts"
    __table_args__ = {"schema": "quality"}

    department: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    dept_head_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("identity.users.id"), nullable=True)
    qa_staff_ids: Mapped[list | None] = mapped_column(ARRAY(Text), nullable=True)
    gmp_staff_ids: Mapped[list | None] = mapped_column(ARRAY(Text), nullable=True)
    production_head_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("identity.users.id"), nullable=True)
    quality_head_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("identity.users.id"), nullable=True)
    additional_contacts: Mapped[list | None] = mapped_column(ARRAY(Text), nullable=True)
    is_production_workshop: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False, server_default="false")


class DepartmentWeeklyConfirmation(BaseModel):
    __tablename__ = "department_weekly_confirmations"
    __table_args__ = (
        UniqueConstraint("department", "week_key", name="uq_dept_weekly_confirmation"),
        {"schema": "quality"},
    )

    department: Mapped[str] = mapped_column(String(255), nullable=False)
    week_key: Mapped[str] = mapped_column(String(20), nullable=False)
    production_status: Mapped[str] = mapped_column(String(20), nullable=False)
    deviation_status: Mapped[str] = mapped_column(String(50), nullable=False, default="unsubmitted", server_default="unsubmitted")
    confirmed_by_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("identity.users.id"), nullable=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AttachmentReview(BaseModel):
    __tablename__ = "attachment_reviews"
    __table_args__ = {"schema": "quality"}

    deviation_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("quality.deviations.id"), nullable=True)
    capa_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("quality.capas.id"), nullable=True)
    attachment_url: Mapped[str] = mapped_column(String(500), nullable=False)
    reviewer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("identity.users.id"), nullable=False)
    review_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", server_default="pending")
