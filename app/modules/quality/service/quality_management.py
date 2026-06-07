"""Quality management business logic."""

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.quality.models import (
    AttachmentReview,
    CAPA,
    DepartmentContact,
    DepartmentWeeklyConfirmation,
    Deviation,
)
from app.modules.quality.schemas import (
    AttachmentReviewOut,
    CapaApprovalRequest,
    CapaDetail,
    CapaListItem,
    CapaStatistics,
    ConfirmProductionStatusRequest,
    CreateCapaRequest,
    CreateDepartmentContactRequest,
    CreateDeviationRequest,
    DeviationDetail,
    DeviationListItem,
    DeviationStatistics,
    SubmitInvestigationRequest,
    SubmitReviewRequest,
    UpdateCapaRequest,
    UpdateDepartmentContactRequest,
    UpdateDeviationRequest,
)


# Workflow constants
APPROVAL_STEP_ORDER = [
    "ai_analysis",
    "investigation",
    "dept_head_review",
    "cross_dept_head_review",
    "qa_review",
    "qa_head_review",
    "quality_head_review",
]

APPROVAL_STEP_LABELS = {
    "ai_analysis": "AI分析",
    "investigation": "调查",
    "dept_head_review": "部门负责人审核",
    "cross_dept_head_review": "跨部门负责人审核",
    "qa_review": "所属QA审核",
    "qa_head_review": "QA负责人审核",
    "quality_head_review": "质量负责人审核",
}

STATUS_TO_STEP = {
    "pending_ai_analysis": "ai_analysis",
    "pending_investigation": "investigation",
    "pending_dept_head_review": "dept_head_review",
    "pending_cross_dept_head_review": "cross_dept_head_review",
    "pending_qa_review": "qa_review",
    "pending_qa_head_review": "qa_head_review",
    "pending_quality_head_review": "quality_head_review",
}

STEP_TO_NEXT_STATUS = {
    "ai_analysis": "pending_investigation",
    "investigation": "pending_dept_head_review",
    "dept_head_review": "pending_cross_dept_head_review",
    "cross_dept_head_review": "pending_qa_review",
    "qa_review": "pending_qa_head_review",
    "qa_head_review": "pending_quality_head_review",
    "quality_head_review": "pending_final_code",
}

STEP_ROLE_LABELS = {
    "ai_analysis": "AI系统",
    "investigation": "调查人",
    "dept_head_review": "部门负责人",
    "cross_dept_head_review": "跨部门负责人",
    "qa_review": "所属QA",
    "qa_head_review": "QA负责人",
    "quality_head_review": "质量负责人",
}

STATUS_TO_PENDING = {
    "ai_analysis": "pending_ai_analysis",
    "investigation": "pending_investigation",
    "dept_head_review": "pending_dept_head_review",
    "cross_dept_head_review": "pending_cross_dept_head_review",
    "qa_review": "pending_qa_review",
    "qa_head_review": "pending_qa_head_review",
    "quality_head_review": "pending_quality_head_review",
}


# ============ Deviation Service ============
async def get_deviation_list(
    db: AsyncSession,
    status: str | None = None,
    level: str | None = None,
    department: str | None = None,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict[str, Any]:
    query = select(Deviation).where(Deviation.is_deleted == False)
    count_query = select(func.count()).select_from(Deviation).where(Deviation.is_deleted == False)

    if status:
        query = query.where(Deviation.status == status)
        count_query = count_query.where(Deviation.status == status)
    if level:
        query = query.where(Deviation.level == level)
        count_query = count_query.where(Deviation.level == level)
    if department:
        query = query.where(Deviation.department == department)
        count_query = count_query.where(Deviation.department == department)
    if keyword:
        query = query.where(Deviation.title.ilike(f"%{keyword}%"))
        count_query = count_query.where(Deviation.title.ilike(f"%{keyword}%"))

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    query = query.order_by(Deviation.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "items": [DeviationListItem.model_validate(item).model_dump() for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


async def get_deviation_detail(db: AsyncSession, deviation_id: uuid.UUID) -> DeviationDetail:
    result = await db.execute(select(Deviation).where(Deviation.id == deviation_id, Deviation.is_deleted == False))
    deviation = result.scalar_one_or_none()
    if not deviation:
        raise ValueError(f"Deviation {deviation_id} not found")
    return DeviationDetail.model_validate(deviation)


async def create_deviation(db: AsyncSession, data: CreateDeviationRequest, user_id: str) -> dict[str, str]:
    deviation = Deviation(
        deviation_code=f"DEV-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}",
        title=data.title,
        department=data.department,
        discovery_date=datetime.fromisoformat(data.discovery_date) if data.discovery_date else None,
        discovery_time=data.discovery_time,
        discovery_location=data.discovery_location,
        level=data.level,
        root_cause_category=data.root_cause_category,
        description=data.description,
        immediate_actions=data.immediate_actions,
        attachments=data.attachments,
        affected_items=data.affected_items,
        batch_number=data.batch_number,
        handler=data.handler,
        needs_cross_dept_review=data.needs_cross_dept_review,
        cross_dept_reviewers=[r.model_dump() for r in data.cross_dept_reviewers] if data.cross_dept_reviewers else [],
        status="draft",
        status_updated_at=datetime.now(timezone.utc),
    )
    db.add(deviation)
    await db.commit()
    await db.refresh(deviation)
    return {"id": str(deviation.id), "code": deviation.deviation_code}


async def update_deviation(db: AsyncSession, deviation_id: uuid.UUID, data: UpdateDeviationRequest, user_id: str) -> dict[str, bool]:
    result = await db.execute(select(Deviation).where(Deviation.id == deviation_id, Deviation.is_deleted == False))
    deviation = result.scalar_one_or_none()
    if not deviation:
        raise ValueError(f"Deviation {deviation_id} not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field in ["ai_analysis", "investigation_records", "review_opinions", "cross_dept_reviewers", "report_versions"]:
            setattr(deviation, field, value)
        elif field == "discovery_date" and value:
            setattr(deviation, field, datetime.fromisoformat(value))
        else:
            setattr(deviation, field, value)

    deviation.updated_at = datetime.now(timezone.utc)
    if data.status:
        deviation.status_updated_at = datetime.now(timezone.utc)

    await db.commit()
    return {"success": True}


async def delete_deviation(db: AsyncSession, deviation_id: uuid.UUID) -> dict[str, bool]:
    result = await db.execute(select(Deviation).where(Deviation.id == deviation_id, Deviation.is_deleted == False))
    deviation = result.scalar_one_or_none()
    if not deviation:
        raise ValueError(f"Deviation {deviation_id} not found")
    deviation.is_deleted = True
    deviation.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return {"success": True}


async def submit_investigation(db: AsyncSession, deviation_id: uuid.UUID, data: SubmitInvestigationRequest, user_id: str) -> dict[str, bool]:
    result = await db.execute(select(Deviation).where(Deviation.id == deviation_id, Deviation.is_deleted == False))
    deviation = result.scalar_one_or_none()
    if not deviation:
        raise ValueError(f"Deviation {deviation_id} not found")
    if deviation.status != "pending_investigation":
        raise ValueError("只有待调查状态的偏差才能提交调查报告")

    if data.description:
        deviation.description = data.description
    if data.investigation_records:
        deviation.investigation_records = data.investigation_records

    deviation.status = "pending_dept_head_review"
    deviation.status_updated_at = datetime.now(timezone.utc)
    deviation.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return {"success": True}


async def submit_review(db: AsyncSession, deviation_id: uuid.UUID, data: SubmitReviewRequest, user_id: str) -> dict[str, bool]:
    result = await db.execute(select(Deviation).where(Deviation.id == deviation_id, Deviation.is_deleted == False))
    deviation = result.scalar_one_or_none()
    if not deviation:
        raise ValueError(f"Deviation {deviation_id} not found")

    current_step = STATUS_TO_STEP.get(deviation.status)
    if not current_step:
        raise ValueError("当前状态不在审核流程中")
    if current_step != data.step:
        raise ValueError("当前需要完成的审核步骤与提交的不一致")

    review_opinions = deviation.review_opinions or []
    new_opinion = {
        "content": data.content,
        "author": user_id,
        "step": data.step,
        "result": data.result,
        "createTime": datetime.now(timezone.utc).isoformat(),
    }
    review_opinions.append(new_opinion)

    if data.result == "rejected":
        deviation.status = "returned"
        deviation.returned_step = data.step
        deviation.review_opinions = review_opinions
        deviation.status_updated_at = datetime.now(timezone.utc)
        deviation.updated_at = datetime.now(timezone.utc)
        await db.commit()
        return {"success": True}

    next_status = STEP_TO_NEXT_STATUS.get(data.step)
    if not next_status:
        raise ValueError("无法确定下一步状态")

    if data.step == "qa_review" and data.result == "approved" and data.reason_category:
        deviation.root_cause_category = data.reason_category
    if data.step == "qa_head_review" and data.deviation_level:
        deviation.level = data.deviation_level

    deviation.status = next_status
    deviation.review_opinions = review_opinions
    deviation.status_updated_at = datetime.now(timezone.utc)
    deviation.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return {"success": True}


async def submit_final_code(db: AsyncSession, deviation_id: uuid.UUID, final_code: str, user_id: str) -> dict[str, bool]:
    result = await db.execute(select(Deviation).where(Deviation.id == deviation_id, Deviation.is_deleted == False))
    deviation = result.scalar_one_or_none()
    if not deviation:
        raise ValueError(f"Deviation {deviation_id} not found")
    if deviation.status != "pending_final_code":
        raise ValueError("当前状态不允许提交最终编号")
    if not final_code or not final_code.strip():
        raise ValueError("最终编号不能为空")

    deviation.final_code = final_code.strip()
    deviation.status = "closed"
    deviation.status_updated_at = datetime.now(timezone.utc)
    deviation.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return {"success": True}


async def resubmit_deviation(db: AsyncSession, deviation_id: uuid.UUID, user_id: str) -> dict[str, bool]:
    result = await db.execute(select(Deviation).where(Deviation.id == deviation_id, Deviation.is_deleted == False))
    deviation = result.scalar_one_or_none()
    if not deviation:
        raise ValueError(f"Deviation {deviation_id} not found")
    if deviation.status != "returned":
        raise ValueError("只有退回状态的偏差才能重新提交")

    returned_step = deviation.returned_step
    target_status = STATUS_TO_PENDING.get(returned_step, "pending_investigation") if returned_step else "pending_investigation"

    deviation.status = target_status
    deviation.returned_step = None
    deviation.status_updated_at = datetime.now(timezone.utc)
    deviation.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return {"success": True}


# ============ CAPA Service ============
async def get_capa_list(
    db: AsyncSession,
    status: str | None = None,
    source: str | None = None,
    category: str | None = None,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict[str, Any]:
    query = select(CAPA).where(CAPA.is_deleted == False)
    count_query = select(func.count()).select_from(CAPA).where(CAPA.is_deleted == False)

    if status:
        query = query.where(CAPA.status == status)
        count_query = count_query.where(CAPA.status == status)
    if source:
        query = query.where(CAPA.source == source)
        count_query = count_query.where(CAPA.source == source)
    if category:
        query = query.where(CAPA.category == category)
        count_query = count_query.where(CAPA.category == category)
    if keyword:
        query = query.where(CAPA.title.ilike(f"%{keyword}%"))
        count_query = count_query.where(CAPA.title.ilike(f"%{keyword}%"))

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    query = query.order_by(CAPA.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "items": [CapaListItem.model_validate(item).model_dump() for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


async def get_capa_detail(db: AsyncSession, capa_id: uuid.UUID) -> CapaDetail:
    result = await db.execute(select(CAPA).where(CAPA.id == capa_id, CAPA.is_deleted == False))
    capa = result.scalar_one_or_none()
    if not capa:
        raise ValueError(f"CAPA {capa_id} not found")
    return CapaDetail.model_validate(capa)


async def create_capa(db: AsyncSession, data: CreateCapaRequest, user_id: str) -> dict[str, str]:
    capa = CAPA(
        capa_code=f"CAPA-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}",
        title=data.title,
        deviation_id=data.deviation_id,
        source=data.source,
        source_code=data.source_code,
        category=data.category,
        root_cause_category=data.root_cause_category,
        non_conformity_description=data.non_conformity_description,
        root_cause_analysis=data.root_cause_analysis,
        capa_content=data.capa_content,
        capa_items=[item.model_dump() for item in data.capa_items] if data.capa_items else [],
        executors=data.executors,
        expected_completion_date=datetime.fromisoformat(data.expected_completion_date) if data.expected_completion_date else None,
        reporter=data.reporter,
        status="draft",
        status_updated_at=datetime.now(timezone.utc),
    )
    db.add(capa)
    await db.commit()
    await db.refresh(capa)
    return {"id": str(capa.id), "code": capa.capa_code}


async def update_capa(db: AsyncSession, capa_id: uuid.UUID, data: UpdateCapaRequest, user_id: str) -> dict[str, bool]:
    result = await db.execute(select(CAPA).where(CAPA.id == capa_id, CAPA.is_deleted == False))
    capa = result.scalar_one_or_none()
    if not capa:
        raise ValueError(f"CAPA {capa_id} not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field in ["capa_items", "execution_tracks", "dept_head_confirmations", "report_versions"]:
            setattr(capa, field, value)
        elif field in ["expected_completion_date", "evaluation_deadline", "evaluation_confirm_date", "closure_date", "qa_review_time", "q_head_approval_time"] and value:
            setattr(capa, field, datetime.fromisoformat(value))
        else:
            setattr(capa, field, value)

    capa.updated_at = datetime.now(timezone.utc)
    if data.status:
        capa.status_updated_at = datetime.now(timezone.utc)

    await db.commit()
    return {"success": True}


async def delete_capa(db: AsyncSession, capa_id: uuid.UUID) -> dict[str, bool]:
    result = await db.execute(select(CAPA).where(CAPA.id == capa_id, CAPA.is_deleted == False))
    capa = result.scalar_one_or_none()
    if not capa:
        raise ValueError(f"CAPA {capa_id} not found")
    capa.is_deleted = True
    capa.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return {"success": True}


# ============ Department Contact Service ============
async def get_department_contact_list(db: AsyncSession, page: int = 1, page_size: int = 20) -> dict[str, Any]:
    query = select(DepartmentContact).where(DepartmentContact.is_deleted == False)
    count_query = select(func.count()).select_from(DepartmentContact).where(DepartmentContact.is_deleted == False)

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    query = query.order_by(DepartmentContact.department).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "items": [item.__dict__ for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


async def upsert_department_contact(db: AsyncSession, data: CreateDepartmentContactRequest | UpdateDepartmentContactRequest, department: str | None, user_id: str) -> dict[str, bool]:
    if department:
        result = await db.execute(select(DepartmentContact).where(DepartmentContact.department == department, DepartmentContact.is_deleted == False))
        contact = result.scalar_one_or_none()
        if contact:
            update_data = data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(contact, field, value)
            contact.updated_at = datetime.now(timezone.utc)
            await db.commit()
            return {"success": True}

    contact = DepartmentContact(
        department=department or data.department,
        dept_head_id=data.dept_head_id,
        qa_staff_ids=data.qa_staff_ids,
        gmp_staff_ids=data.gmp_staff_ids,
        production_head_id=data.production_head_id,
        quality_head_id=data.quality_head_id,
        additional_contacts=data.additional_contacts,
        is_production_workshop=data.is_production_workshop if hasattr(data, 'is_production_workshop') else False,
    )
    db.add(contact)
    await db.commit()
    return {"success": True}


async def delete_department_contact(db: AsyncSession, contact_id: uuid.UUID) -> dict[str, bool]:
    result = await db.execute(select(DepartmentContact).where(DepartmentContact.id == contact_id, DepartmentContact.is_deleted == False))
    contact = result.scalar_one_or_none()
    if not contact:
        raise ValueError(f"DepartmentContact {contact_id} not found")
    contact.is_deleted = True
    contact.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return {"success": True}


# ============ Statistics ============
async def get_deviation_statistics(db: AsyncSession) -> DeviationStatistics:
    total_result = await db.execute(select(func.count()).select_from(Deviation).where(Deviation.is_deleted == False))
    total = total_result.scalar_one()

    pending_result = await db.execute(
        select(func.count())
        .select_from(Deviation)
        .where(Deviation.is_deleted == False, Deviation.status.like("pending_%"))
    )
    pending = pending_result.scalar_one()

    dept_result = await db.execute(
        select(Deviation.department, func.count())
        .where(Deviation.is_deleted == False)
        .group_by(Deviation.department)
    )
    department_distribution = [{"name": row[0] or "未知", "count": row[1]} for row in dept_result.all()]

    status_result = await db.execute(
        select(Deviation.status, func.count())
        .where(Deviation.is_deleted == False)
        .group_by(Deviation.status)
    )
    status_distribution = [{"status": row[0], "count": row[1]} for row in status_result.all()]

    step_breakdown = []
    for step in APPROVAL_STEP_ORDER:
        pending_status = STATUS_TO_PENDING.get(step)
        match = next((s for s in status_distribution if s["status"] == pending_status), None)
        step_breakdown.append({
            "step": step,
            "label": APPROVAL_STEP_LABELS.get(step, step),
            "roleLabel": STEP_ROLE_LABELS.get(step, ""),
            "count": match["count"] if match else 0,
        })

    return DeviationStatistics(
        total=total,
        pending=pending,
        departmentDistribution=department_distribution,
        statusDistribution=status_distribution,
        stepBreakdown=step_breakdown,
    )


async def get_capa_statistics(db: AsyncSession) -> CapaStatistics:
    total_result = await db.execute(select(func.count()).select_from(CAPA).where(CAPA.is_deleted == False))
    total = total_result.scalar_one()

    status_result = await db.execute(
        select(CAPA.status, func.count())
        .where(CAPA.is_deleted == False)
        .group_by(CAPA.status)
    )
    status_distribution = [{"status": row[0], "count": row[1]} for row in status_result.all()]

    source_result = await db.execute(
        select(CAPA.source, func.count())
        .where(CAPA.is_deleted == False)
        .group_by(CAPA.source)
    )
    source_distribution = [{"source": row[0] or "未知", "count": row[1]} for row in source_result.all()]

    return CapaStatistics(
        total=total,
        statusDistribution=status_distribution,
        sourceDistribution=source_distribution,
    )


# ============ Attachment Reviews ============
async def list_attachment_reviews(
    db: AsyncSession,
    deviation_id: uuid.UUID | None = None,
    capa_id: uuid.UUID | None = None,
    attachment_url: str | None = None,
) -> list[dict]:
    """List attachment reviews with optional filters."""
    query = select(AttachmentReview).where(AttachmentReview.is_deleted == False)
    if deviation_id:
        query = query.where(AttachmentReview.deviation_id == deviation_id)
    if capa_id:
        query = query.where(AttachmentReview.capa_id == capa_id)
    if attachment_url:
        query = query.where(AttachmentReview.attachment_url == attachment_url)
    query = query.order_by(AttachmentReview.review_time.desc())
    
    result = await db.execute(query)
    items = result.scalars().all()
    return [AttachmentReviewOut.model_validate(item).model_dump() for item in items]


async def create_attachment_review(
    db: AsyncSession,
    data,
    reviewer_id: str,
) -> dict:
    """Create a new attachment review."""
    review = AttachmentReview(
        deviation_id=data.deviation_id,
        capa_id=data.capa_id,
        attachment_url=data.attachment_url,
        content=data.content,
        reviewer_id=reviewer_id,
        review_time=datetime.now(timezone.utc),
    )
    db.add(review)
    await db.flush()
    await db.refresh(review)
    return AttachmentReviewOut.model_validate(review).model_dump()


async def delete_attachment_review(db: AsyncSession, review_id: uuid.UUID) -> None:
    """Soft-delete an attachment review."""
    review = await db.get(AttachmentReview, review_id)
    if not review:
        raise ValueError("Attachment review not found")
    review.is_deleted = True
    await db.flush()
