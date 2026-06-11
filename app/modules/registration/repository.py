"""Registration database queries live here."""

from uuid import UUID

from sqlalchemy import asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.registration.models import AuthorizationLetter


class AuthorizationLetterRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, letter_id: UUID) -> AuthorizationLetter | None:
        result = await self.session.execute(
            select(AuthorizationLetter).where(
                AuthorizationLetter.id == letter_id,
                AuthorizationLetter.is_deleted.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def list_letters(
        self,
        *,
        product_name: str | None = None,
        preparation_unit: str | None = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[AuthorizationLetter], int]:
        stmt = select(AuthorizationLetter).where(
            AuthorizationLetter.is_deleted.is_(False)
        )

        if product_name:
            stmt = stmt.where(
                AuthorizationLetter.product_name.ilike(f"%{product_name}%")
            )
        if preparation_unit:
            stmt = stmt.where(
                AuthorizationLetter.preparation_unit.ilike(f"%{preparation_unit}%")
            )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar() or 0

        default_sort = AuthorizationLetter.created_at
        sort_column = getattr(AuthorizationLetter, sort_by, default_sort)
        order_func = desc if sort_order == "desc" else asc
        stmt = stmt.order_by(order_func(sort_column))
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        result = await self.session.execute(stmt)
        return list(result.scalars().all()), total

    async def create(self, letter: AuthorizationLetter) -> AuthorizationLetter:
        self.session.add(letter)
        await self.session.flush()
        await self.session.refresh(letter)
        return letter

    async def soft_delete(self, letter: AuthorizationLetter) -> None:
        letter.is_deleted = True
        await self.session.flush()
