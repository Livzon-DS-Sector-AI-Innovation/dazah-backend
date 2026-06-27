"""Procurement database queries live here."""

from uuid import UUID

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.procurement.models import InvoiceRecognitionRecord


class InvoiceRecognitionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        record: InvoiceRecognitionRecord,
    ) -> InvoiceRecognitionRecord:
        self.session.add(record)
        await self.session.flush()
        return record

    async def find_duplicate(
        self,
        *,
        duplicate_key: str | None,
        source_file_sha256: str | None,
    ) -> InvoiceRecognitionRecord | None:
        filters = []
        if duplicate_key:
            filters.append(InvoiceRecognitionRecord.duplicate_key == duplicate_key)
        if source_file_sha256:
            filters.append(
                InvoiceRecognitionRecord.source_file_sha256 == source_file_sha256
            )
        if not filters:
            return None

        result = await self.session.execute(
            select(InvoiceRecognitionRecord)
            .where(
                InvoiceRecognitionRecord.is_deleted.is_(False),
                or_(*filters),
            )
            .order_by(InvoiceRecognitionRecord.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def list_records(
        self,
        *,
        keyword: str | None = None,
        seller_name: str | None = None,
        invoice_number: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[InvoiceRecognitionRecord], int]:
        base_query = select(InvoiceRecognitionRecord).where(
            InvoiceRecognitionRecord.is_deleted.is_(False)
        )
        count_query = select(func.count(InvoiceRecognitionRecord.id)).where(
            InvoiceRecognitionRecord.is_deleted.is_(False)
        )

        if seller_name:
            seller_filter = InvoiceRecognitionRecord.seller_name.ilike(
                f"%{seller_name}%"
            )
            base_query = base_query.where(seller_filter)
            count_query = count_query.where(seller_filter)
        if invoice_number:
            invoice_filter = InvoiceRecognitionRecord.invoice_number == invoice_number
            base_query = base_query.where(invoice_filter)
            count_query = count_query.where(invoice_filter)
        if keyword:
            like_pattern = f"%{keyword}%"
            keyword_filter = or_(
                InvoiceRecognitionRecord.file_name.ilike(like_pattern),
                InvoiceRecognitionRecord.invoice_number.ilike(like_pattern),
                InvoiceRecognitionRecord.seller_name.ilike(like_pattern),
            )
            base_query = base_query.where(keyword_filter)
            count_query = count_query.where(keyword_filter)

        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        result = await self.session.execute(
            base_query.order_by(InvoiceRecognitionRecord.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    async def delete_record(self, record_id: UUID) -> bool:
        stmt = (
            update(InvoiceRecognitionRecord)
            .where(
                InvoiceRecognitionRecord.id == record_id,
                InvoiceRecognitionRecord.is_deleted.is_(False),
            )
            .values(is_deleted=True)
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def batch_delete_records(self, record_ids: list[UUID]) -> int:
        if not record_ids:
            return 0

        stmt = (
            update(InvoiceRecognitionRecord)
            .where(
                InvoiceRecognitionRecord.id.in_(record_ids),
                InvoiceRecognitionRecord.is_deleted.is_(False),
            )
            .values(is_deleted=True)
        )
        result = await self.session.execute(stmt)
        return result.rowcount
