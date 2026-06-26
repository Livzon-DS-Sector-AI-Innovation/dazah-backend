"""Registration ledger schemas."""

from datetime import date, datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ── Domestic Approval ──────────────────────────────────────────────

class DomesticApprovalBase(BaseModel):
    product_name: str
    certificate_name: Optional[str] = None
    batch_no: Optional[str] = None
    issuing_authority: Optional[str] = None
    issue_date: Optional[date] = None
    valid_until: Optional[date] = None
    product_scope: Optional[str] = None
    quality_standard: Optional[str] = None
    registration_no: Optional[str] = None
    is_expired: Optional[str] = None
    production_workshop: Optional[str] = None
    product_validity: Optional[str] = None
    storage_condition: Optional[str] = None


class DomesticApprovalCreate(DomesticApprovalBase):
    pass


class DomesticApprovalUpdate(DomesticApprovalBase):
    product_name: Optional[str] = None


class DomesticApprovalResponse(DomesticApprovalBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Overseas Approval ─────────────────────────────────────────────

class OverseasApprovalBase(BaseModel):
    product_name: str
    certificate_name: Optional[str] = None
    batch_no: Optional[str] = None
    issuing_authority: Optional[str] = None
    issue_date: Optional[date] = None
    valid_until: Optional[date] = None
    product_scope: Optional[str] = None
    quality_standard: Optional[str] = None
    is_expired: Optional[str] = None
    production_workshop: Optional[str] = None
    product_validity: Optional[str] = None
    storage_condition: Optional[str] = None


class OverseasApprovalCreate(OverseasApprovalBase):
    pass


class OverseasApprovalUpdate(OverseasApprovalBase):
    product_name: Optional[str] = None


class OverseasApprovalResponse(OverseasApprovalBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── International Review ───────────────────────────────────────────

class InternationalReviewBase(BaseModel):
    product_name: str
    approved_countries: Optional[str] = None
    approved_country_count: Optional[int] = None
    approved_clients: Optional[str] = None
    approved_client_count: Optional[int] = None
    reviewing_countries: Optional[str] = None
    reviewing_country_count: Optional[int] = None
    reviewing_clients: Optional[str] = None
    reviewing_client_count: Optional[int] = None


class InternationalReviewCreate(InternationalReviewBase):
    pass


class InternationalReviewUpdate(InternationalReviewBase):
    product_name: Optional[str] = None


class InternationalReviewResponse(InternationalReviewBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── COPP Certificate ───────────────────────────────────────────────

class CoppCertificateBase(BaseModel):
    product_name: str
    certificate_name: Optional[str] = None
    batch_no: Optional[str] = None
    issuing_authority: Optional[str] = None
    issue_date: Optional[date] = None
    valid_until: Optional[date] = None
    product_scope: Optional[str] = None
    applicable_countries: Optional[str] = None
    is_expired: Optional[str] = None


class CoppCertificateCreate(CoppCertificateBase):
    pass


class CoppCertificateUpdate(CoppCertificateBase):
    product_name: Optional[str] = None


class CoppCertificateResponse(CoppCertificateBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── WC Certificate ─────────────────────────────────────────────────

class WcCertificateBase(BaseModel):
    product_name: str
    certificate_name: Optional[str] = None
    batch_no: Optional[str] = None
    issuing_authority: Optional[str] = None
    issue_date: Optional[date] = None
    valid_until: Optional[date] = None
    product_scope: Optional[str] = None
    is_expired: Optional[str] = None


class WcCertificateCreate(WcCertificateBase):
    pass


class WcCertificateUpdate(WcCertificateBase):
    product_name: Optional[str] = None


class WcCertificateResponse(WcCertificateBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Ledger Summary (for Dashboard) ─────────────────────────────────

class LedgerSummary(BaseModel):
    domestic_count: int
    overseas_count: int
    overseas_countries: int
    international_review_count: int
    copp_count: int
    wc_count: int
    reviewing_count: int
    planned_count: int
