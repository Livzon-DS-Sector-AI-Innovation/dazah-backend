"""Pydantic schemas for quality management."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ============ Shared ============
class PageParams(BaseModel):
    page: int = 1
    page_size: int = 20


# ============ Deviation ============
class AiAnalysis(BaseModel):
    description: str | None = None
    reason: str | None = None
    riskAssessment: str | None = None
    capaSuggestion: str | None = None


class InvestigationRecord(BaseModel):
    nonconformityDescription: str | None = None
    rootCauseAnalysis: str | None = None
    riskAssessment: str | None = None
    urgentMeasures: str | None = None
    content: str | None = None
    author: str = ""
    department: str | None = None
    createTime: str = ""
    attachments: list[str] | None = None
    isModified: bool = False
    modifyTime: str | None = None
    capaProposals: list[dict] | None = None


class ReviewOpinion(BaseModel):
    content: str = ""
    author: str = ""
    step: str = ""
    result: str = "approved"
    createTime: str = ""


class CrossDeptReviewer(BaseModel):
    department: str = ""
    investigators: list[str] = []


class DeviationListItem(BaseModel):
    id: uuid.UUID
    deviation_code: str
    final_code: str | None = None
    title: str
    department: str | None = None
    discovery_date: datetime | None = None
    status: str
    level: str | None = None
    root_cause_category: str | None = None
    reporter_id: uuid.UUID | None = None
    handler: str | None = None
    created_at: datetime
    status_updated_at: datetime | None = None
    returned_step: str | None = None

    class Config:
        from_attributes = True


class DeviationDetail(BaseModel):
    id: uuid.UUID
    deviation_code: str
    final_code: str | None = None
    title: str
    department: str | None = None
    discovery_date: datetime | None = None
    discovery_time: str | None = None
    discovery_location: str | None = None
    status: str
    level: str | None = None
    root_cause_category: str | None = None
    description: str | None = None
    immediate_actions: str | None = None
    reporter_id: uuid.UUID | None = None
    handler: str | None = None
    discoverer: str | None = None
    ai_analysis: dict | None = None
    investigation_records: list | None = None
    review_opinions: list | None = None
    attachments: list[str] | None = None
    needs_cross_dept_review: bool | None = True
    cross_dept_reviewers: list | None = None
    affected_items: str | None = None
    batch_number: str | None = None
    returned_step: str | None = None
    status_updated_at: datetime | None = None
    report_content: str | None = None
    report_versions: list | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CreateDeviationRequest(BaseModel):
    title: str
    department: str | None = None
    discovery_date: str | None = None
    discovery_time: str | None = None
    discovery_location: str | None = None
    level: str | None = None
    root_cause_category: str | None = None
    description: str | None = None
    immediate_actions: str | None = None
    attachments: list[str] | None = None
    affected_items: str | None = None
    batch_number: str | None = None
    handler: str | None = None
    needs_cross_dept_review: bool | None = True
    cross_dept_reviewers: list[CrossDeptReviewer] | None = None


class UpdateDeviationRequest(BaseModel):
    title: str | None = None
    status: str | None = None
    level: str | None = None
    department: str | None = None
    discovery_date: str | None = None
    discovery_time: str | None = None
    discovery_location: str | None = None
    root_cause_category: str | None = None
    description: str | None = None
    immediate_actions: str | None = None
    ai_analysis: dict | None = None
    investigation_records: list | None = None
    review_opinions: list | None = None
    attachments: list[str] | None = None
    final_code: str | None = None
    handler: str | None = None
    discoverer: str | None = None
    needs_cross_dept_review: bool | None = None
    cross_dept_reviewers: list[CrossDeptReviewer] | None = None
    affected_items: str | None = None
    batch_number: str | None = None
    returned_step: str | None = None
    report_content: str | None = None
    report_versions: list | None = None


class SubmitReviewRequest(BaseModel):
    step: str
    result: str = "approved"
    content: str = ""
    reason_category: str | None = None
    deviation_level: str | None = None


class SubmitInvestigationRequest(BaseModel):
    description: str | None = None
    investigation_records: list | None = None
    nonconformity_description: str | None = None
    root_cause_analysis: str | None = None
    risk_assessment: str | None = None
    urgent_measures: str | None = None
    capa_proposals: list[dict] | None = None


# ============ CAPA ============
class CapaItem(BaseModel):
    content: str = ""
    executors: str = ""
    expectedCompletionDate: str = ""


class DeptHeadConfirmation(BaseModel):
    department: str = ""
    deptHeadUserId: str = ""
    result: str = ""
    opinion: str = ""
    confirmTime: str = ""


class ExecutionTrack(BaseModel):
    executionStatus: str = ""
    qaConfirmer: str | None = None
    qaConfirmDate: str | None = None


class CapaListItem(BaseModel):
    id: uuid.UUID
    capa_code: str
    final_code: str | None = None
    title: str | None = None
    status: str
    source: str | None = None
    source_code: str | None = None
    category: str | None = None
    root_cause_category: str | None = None
    deviation_id: uuid.UUID | None = None
    expected_completion_date: datetime | None = None
    created_at: datetime
    status_updated_at: datetime | None = None

    class Config:
        from_attributes = True


class CapaDetail(BaseModel):
    id: uuid.UUID
    capa_code: str
    final_code: str | None = None
    title: str | None = None
    status: str
    deviation_id: uuid.UUID | None = None
    source: str | None = None
    source_code: str | None = None
    category: str | None = None
    root_cause_category: str | None = None
    non_conformity_description: str | None = None
    root_cause_analysis: str | None = None
    capa_content: str | None = None
    capa_items: list | None = None
    executors: list[str] | None = None
    expected_completion_date: datetime | None = None
    qa_reviewer_id: uuid.UUID | None = None
    qa_review_opinion: str | None = None
    qa_review_time: datetime | None = None
    q_head_approver_id: uuid.UUID | None = None
    q_head_approval_opinion: str | None = None
    q_head_approval_time: datetime | None = None
    execution_status: str | None = None
    execution_tracks: list | None = None
    dept_head_confirmations: list | None = None
    evaluation_result: str | None = None
    evaluation_target: str | None = None
    evaluation_deadline: datetime | None = None
    evaluation_confirmer_id: uuid.UUID | None = None
    evaluation_confirm_date: datetime | None = None
    closure_date: datetime | None = None
    closure_remark: str | None = None
    report_content: str | None = None
    report_versions: list | None = None
    returned_step: str | None = None
    status_updated_at: datetime | None = None
    reporter: str | None = None
    reason_category: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CreateCapaRequest(BaseModel):
    title: str | None = None
    deviation_id: uuid.UUID | None = None
    source: str | None = None
    source_code: str | None = None
    category: str | None = None
    root_cause_category: str | None = None
    non_conformity_description: str | None = None
    root_cause_analysis: str | None = None
    capa_content: str | None = None
    capa_items: list[CapaItem] | None = None
    executors: list[str] | None = None
    expected_completion_date: str | None = None
    reporter: str | None = None


class UpdateCapaRequest(BaseModel):
    title: str | None = None
    status: str | None = None
    source: str | None = None
    source_code: str | None = None
    category: str | None = None
    root_cause_category: str | None = None
    non_conformity_description: str | None = None
    root_cause_analysis: str | None = None
    capa_content: str | None = None
    capa_items: list[CapaItem] | None = None
    executors: list[str] | None = None
    expected_completion_date: str | None = None
    qa_reviewer_id: uuid.UUID | None = None
    qa_review_opinion: str | None = None
    q_head_approver_id: uuid.UUID | None = None
    q_head_approval_opinion: str | None = None
    execution_status: str | None = None
    execution_tracks: list[ExecutionTrack] | None = None
    dept_head_confirmations: list[DeptHeadConfirmation] | None = None
    evaluation_result: str | None = None
    evaluation_target: str | None = None
    evaluation_deadline: str | None = None
    evaluation_confirmer_id: uuid.UUID | None = None
    evaluation_confirm_date: str | None = None
    closure_date: str | None = None
    closure_remark: str | None = None
    final_code: str | None = None
    report_content: str | None = None
    report_versions: list | None = None
    returned_step: str | None = None
    reporter: str | None = None
    reason_category: str | None = None


class CapaApprovalRequest(BaseModel):
    step: str
    result: str = "approved"
    opinion: str = ""


# ============ Department Contact ============
class DepartmentContactOut(BaseModel):
    id: uuid.UUID
    department: str
    dept_head_id: uuid.UUID | None = None
    qa_staff_ids: list[str] | None = None
    gmp_staff_ids: list[str] | None = None
    production_head_id: uuid.UUID | None = None
    quality_head_id: uuid.UUID | None = None
    additional_contacts: list[str] | None = None
    is_production_workshop: bool | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CreateDepartmentContactRequest(BaseModel):
    department: str
    dept_head_id: uuid.UUID | None = None
    qa_staff_ids: list[str] | None = None
    gmp_staff_ids: list[str] | None = None
    production_head_id: uuid.UUID | None = None
    quality_head_id: uuid.UUID | None = None
    additional_contacts: list[str] | None = None
    is_production_workshop: bool | None = None


class UpdateDepartmentContactRequest(BaseModel):
    dept_head_id: uuid.UUID | None = None
    qa_staff_ids: list[str] | None = None
    gmp_staff_ids: list[str] | None = None
    production_head_id: uuid.UUID | None = None
    quality_head_id: uuid.UUID | None = None
    additional_contacts: list[str] | None = None
    is_production_workshop: bool | None = None


# ============ Department Weekly Confirmation ============
class DepartmentWeeklyConfirmationOut(BaseModel):
    id: uuid.UUID
    department: str
    week_key: str
    production_status: str
    deviation_status: str
    confirmed_by_id: uuid.UUID | None = None
    confirmed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConfirmProductionStatusRequest(BaseModel):
    department: str
    week_key: str
    production_status: str
    deviation_status: str = "unsubmitted"


# ============ Attachment Review ============
class AttachmentReviewOut(BaseModel):
    id: uuid.UUID
    deviation_id: uuid.UUID | None = None
    capa_id: uuid.UUID | None = None
    attachment_url: str
    reviewer_id: uuid.UUID
    review_time: datetime | None = None
    content: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ Statistics ============
class StepBreakdownItem(BaseModel):
    step: str
    label: str
    roleLabel: str
    count: int


class DeviationStatistics(BaseModel):
    total: int
    pending: int
    departmentDistribution: list[dict[str, Any]]
    statusDistribution: list[dict[str, Any]]
    stepBreakdown: list[StepBreakdownItem]


class CapaStatistics(BaseModel):
    total: int
    statusDistribution: list[dict[str, Any]]
    sourceDistribution: list[dict[str, Any]]


class CreateAttachmentReviewRequest(BaseModel):
    deviation_id: uuid.UUID | None = None
    capa_id: uuid.UUID | None = None
    attachment_url: str
    content: str
