import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from app.modules.procurement import service as procurement_service
from app.modules.procurement.schemas import (
    PurchaseApprovalRequest,
    PurchaseApprovalResult,
    PurchaseApprovalRole,
    PurchaseApprovalView,
    PurchaseRequestCategory,
    PurchaseRequestCreate,
    PurchaseRequestItemInput,
    PurchaseRequestStatus,
)


class FakeDb:
    async def flush(self) -> None:
        return None


class FakePurchaseRequestRepository:
    requests = {}
    items = {}
    approvals = {}

    def __init__(self, session) -> None:
        self.session = session

    @classmethod
    def reset(cls) -> None:
        cls.requests = {}
        cls.items = {}
        cls.approvals = {}

    async def create(self, request, items):
        request.id = uuid.uuid4()
        request.created_at = datetime.now(UTC)
        request.updated_at = request.created_at
        self.requests[request.id] = request
        for item in items:
            item.id = uuid.uuid4()
            item.purchase_request_id = str(request.id)
            item.created_at = request.created_at
            item.updated_at = request.created_at
        self.items[request.id] = items
        self.approvals[request.id] = []
        return request

    async def get(self, request_id):
        return self.requests.get(request_id)

    async def list_items(self, request_id):
        return self.items.get(request_id, [])

    async def list_approvals(self, request_id):
        return self.approvals.get(request_id, [])

    async def list_requests(
        self,
        *,
        category=None,
        status=None,
        keyword=None,
        page=1,
        page_size=20,
    ):
        records = list(self.requests.values())
        if category:
            records = [record for record in records if record.category == category]
        if status:
            records = [record for record in records if record.status == status]
        if keyword:
            records = [
                record
                for record in records
                if keyword in record.request_department
            ]
        return records[(page - 1) * page_size : page * page_size], len(records)

    async def list_requests_by_approval(
        self,
        *,
        approval_role,
        result,
        category=None,
        keyword=None,
        page=1,
        page_size=20,
    ):
        matching_ids = []
        for request_id, approvals in self.approvals.items():
            if any(
                approval.approval_role == approval_role
                and approval.result == result
                for approval in approvals
            ):
                matching_ids.append(request_id)

        records = [
            self.requests[request_id]
            for request_id in matching_ids
            if request_id in self.requests
        ]
        if category:
            records = [record for record in records if record.category == category]
        if keyword:
            records = [
                record
                for record in records
                if keyword in record.request_department
            ]
        return records[(page - 1) * page_size : page * page_size], len(records)

    async def replace_items(self, request_id, items):
        for item in items:
            item.id = uuid.uuid4()
            item.purchase_request_id = str(request_id)
            item.created_at = datetime.now(UTC)
            item.updated_at = item.created_at
        self.items[request_id] = items

    async def add_approval(self, approval):
        approval.id = uuid.uuid4()
        approval.created_at = datetime.now(UTC)
        approval.updated_at = approval.created_at
        self.approvals.setdefault(uuid.UUID(approval.purchase_request_id), []).append(
            approval
        )
        return approval


@pytest.fixture(autouse=True)
def fake_purchase_request_repository(monkeypatch):
    FakePurchaseRequestRepository.reset()
    monkeypatch.setattr(
        procurement_service,
        "PurchaseRequestRepository",
        FakePurchaseRequestRepository,
    )


def _create_payload() -> PurchaseRequestCreate:
    return PurchaseRequestCreate(
        category=PurchaseRequestCategory.hardware,
        request_department="102一车间",
        request_date=date(2026, 6, 28),
        items=[
            PurchaseRequestItemInput(
                product_name="碳鼓",
                specification="M1005",
                purpose="更换打印机碳鼓",
                material="",
                brand="惠普",
                quantity=Decimal("2"),
                unit="个",
                unit_price=Decimal("60.005"),
                remarks="申购人：郭娇",
            )
        ],
    )


@pytest.mark.anyio
async def test_purchase_request_amount_and_two_step_approval_flow() -> None:
    created = await procurement_service.create_purchase_request(
        FakeDb(),
        _create_payload(),
    )

    assert created.request_date == date(2026, 6, 28)
    assert created.status == PurchaseRequestStatus.draft
    assert created.total_amount == Decimal("120.01")
    assert created.items[0].total_amount == Decimal("120.01")

    submitted = await procurement_service.submit_purchase_request(
        FakeDb(),
        created.id,
    )
    assert submitted.status == PurchaseRequestStatus.pending_department_head

    department_approved = await procurement_service.approve_purchase_request(
        FakeDb(),
        created.id,
        PurchaseApprovalRequest(
            approval_role=PurchaseApprovalRole.department_head,
            approver_name="部门负责人",
            opinion="同意",
            result=PurchaseApprovalResult.approved,
        ),
    )
    assert (
        department_approved.status
        == PurchaseRequestStatus.pending_responsible_leader
    )
    assert department_approved.approvals[0].approval_role == (
        PurchaseApprovalRole.department_head
    )

    leader_approved = await procurement_service.approve_purchase_request(
        FakeDb(),
        created.id,
        PurchaseApprovalRequest(
            approval_role=PurchaseApprovalRole.responsible_leader,
            approver_name="分管领导",
            opinion="同意",
            result=PurchaseApprovalResult.approved,
        ),
    )
    assert leader_approved.status == PurchaseRequestStatus.approved
    assert len(leader_approved.approvals) == 2


@pytest.mark.anyio
async def test_purchase_request_reject_persists_approval_record() -> None:
    created = await procurement_service.create_purchase_request(
        FakeDb(),
        _create_payload(),
    )
    await procurement_service.submit_purchase_request(FakeDb(), created.id)

    rejected = await procurement_service.reject_purchase_request(
        FakeDb(),
        created.id,
        PurchaseApprovalRequest(
            approval_role=PurchaseApprovalRole.department_head,
            approver_name="部门负责人",
            opinion="用途不清",
            result=PurchaseApprovalResult.rejected,
        ),
    )

    assert rejected.status == PurchaseRequestStatus.rejected
    assert rejected.rejected_step == PurchaseApprovalRole.department_head
    assert rejected.approvals[0].result == PurchaseApprovalResult.rejected
    assert rejected.approvals[0].opinion == "用途不清"


@pytest.mark.anyio
async def test_purchase_request_role_approval_views() -> None:
    created = await procurement_service.create_purchase_request(
        FakeDb(),
        _create_payload(),
    )
    await procurement_service.submit_purchase_request(FakeDb(), created.id)
    await procurement_service.approve_purchase_request(
        FakeDb(),
        created.id,
        PurchaseApprovalRequest(
            approval_role=PurchaseApprovalRole.department_head,
            approver_name="部门负责人",
            opinion="同意",
            result=PurchaseApprovalResult.approved,
        ),
    )

    department_completed, department_completed_total = (
        await procurement_service.list_purchase_requests(
            FakeDb(),
            category=PurchaseRequestCategory.hardware.value,
            approval_role=PurchaseApprovalRole.department_head,
            approval_view=PurchaseApprovalView.completed,
        )
    )
    leader_pending, leader_pending_total = (
        await procurement_service.list_purchase_requests(
            FakeDb(),
            category=PurchaseRequestCategory.hardware.value,
            approval_role=PurchaseApprovalRole.responsible_leader,
            approval_view=PurchaseApprovalView.pending,
        )
    )

    assert department_completed_total == 1
    assert department_completed[0].id == created.id
    assert (
        department_completed[0].status
        == PurchaseRequestStatus.pending_responsible_leader
    )
    assert leader_pending_total == 1
    assert leader_pending[0].id == created.id


@pytest.mark.anyio
async def test_purchase_request_role_rejected_view() -> None:
    created = await procurement_service.create_purchase_request(
        FakeDb(),
        _create_payload(),
    )
    await procurement_service.submit_purchase_request(FakeDb(), created.id)
    await procurement_service.reject_purchase_request(
        FakeDb(),
        created.id,
        PurchaseApprovalRequest(
            approval_role=PurchaseApprovalRole.department_head,
            approver_name="部门负责人",
            opinion="用途不清",
            result=PurchaseApprovalResult.rejected,
        ),
    )

    department_rejected, department_rejected_total = (
        await procurement_service.list_purchase_requests(
            FakeDb(),
            category=PurchaseRequestCategory.hardware.value,
            approval_role=PurchaseApprovalRole.department_head,
            approval_view=PurchaseApprovalView.rejected,
        )
    )
    leader_rejected, leader_rejected_total = (
        await procurement_service.list_purchase_requests(
            FakeDb(),
            category=PurchaseRequestCategory.hardware.value,
            approval_role=PurchaseApprovalRole.responsible_leader,
            approval_view=PurchaseApprovalView.rejected,
        )
    )

    assert department_rejected_total == 1
    assert department_rejected[0].id == created.id
    assert department_rejected[0].status == PurchaseRequestStatus.rejected
    assert leader_rejected_total == 0
    assert leader_rejected == []
