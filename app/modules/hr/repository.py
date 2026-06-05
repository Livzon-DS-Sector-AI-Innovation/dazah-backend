"""HR database queries live here."""

from uuid import UUID

from sqlalchemy import asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.hr.models import Department, Employee, OffboardingRecord, Team


class EmployeeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, employee_id: UUID) -> Employee | None:
        result = await self.session.execute(
            select(Employee).where(Employee.id == employee_id, Employee.is_deleted.is_(False))
        )
        return result.scalar_one_or_none()

    async def get_by_employee_number(self, employee_number: str) -> Employee | None:
        result = await self.session.execute(
            select(Employee).where(
                Employee.employee_number == employee_number,
                Employee.is_deleted.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def list_employees(
        self,
        *,
        department: str | None = None,
        status: str | None = None,
        keyword: str | None = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[Employee], int]:
        stmt = select(Employee).where(Employee.is_deleted.is_(False))

        if department:
            stmt = stmt.where(Employee.department == department)
        if status:
            stmt = stmt.where(Employee.status == status)
        else:
            # 默认排除待审批员工，只有显式筛选时才显示
            stmt = stmt.where(Employee.status != "待审批")
        if keyword:
            stmt = stmt.where(
                Employee.name.ilike(f"%{keyword}%")
                | Employee.employee_number.ilike(f"%{keyword}%")
            )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar() or 0

        sort_column = getattr(Employee, sort_by, Employee.created_at)
        order_func = desc if sort_order == "desc" else asc
        stmt = stmt.order_by(order_func(sort_column))
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        result = await self.session.execute(stmt)
        return list(result.scalars().all()), total

    async def create(self, employee: Employee) -> Employee:
        self.session.add(employee)
        await self.session.flush()
        await self.session.refresh(employee)
        return employee

    async def update(self, employee: Employee) -> Employee:
        await self.session.flush()
        await self.session.refresh(employee)
        return employee

    async def upsert_by_employee_number(self, data: dict) -> Employee:
        """Create or update employee by employee_number (used for Feishu sync)."""
        emp = await self.get_by_employee_number(data["employee_number"])
        if emp:
            for key, value in data.items():
                if key != "id" and value is not None:
                    setattr(emp, key, value)
            await self.session.flush()
            await self.session.refresh(emp)
            return emp
        else:
            new_emp = Employee(**{k: v for k, v in data.items() if v is not None})
            self.session.add(new_emp)
            await self.session.flush()
            await self.session.refresh(new_emp)
            return new_emp

    async def get_feishu_record_map(self) -> dict[str, str]:
        """Return {employee_number: feishu_record_id} for all non-deleted employees."""
        result = await self.session.execute(
            select(Employee.employee_number, Employee.feishu_record_id).where(
                Employee.is_deleted.is_(False),
                Employee.feishu_record_id.isnot(None),
            )
        )
        return {row[0]: row[1] for row in result.all()}

    async def count_total(self) -> int:
        result = await self.session.execute(
            select(func.count()).where(Employee.is_deleted.is_(False))
        )
        return result.scalar() or 0

    async def count_synced(self) -> int:
        result = await self.session.execute(
            select(func.count()).where(
                Employee.is_deleted.is_(False),
                Employee.feishu_record_id.isnot(None),
            )
        )
        return result.scalar() or 0

    async def soft_delete(self, employee: Employee) -> None:
        employee.is_deleted = True
        await self.session.flush()


class DepartmentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, department_id: UUID) -> Department | None:
        result = await self.session.execute(
            select(Department).where(Department.id == department_id, Department.is_deleted.is_(False))
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Department | None:
        # 包含已删除记录，确保唯一性检查覆盖软删除数据
        result = await self.session.execute(
            select(Department).where(Department.code == code)
        )
        return result.scalar_one_or_none()

    async def list_departments(
        self,
        *,
        keyword: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Department], int]:
        stmt = select(Department).where(Department.is_deleted.is_(False))

        if keyword:
            stmt = stmt.where(
                Department.name.ilike(f"%{keyword}%")
                | Department.code.ilike(f"%{keyword}%")
            )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = stmt.order_by(asc(Department.created_at))
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        result = await self.session.execute(stmt)
        return list(result.scalars().all()), total

    async def create(self, department: Department) -> Department:
        self.session.add(department)
        await self.session.flush()
        await self.session.refresh(department)
        return department

    async def update(self, department: Department) -> Department:
        await self.session.flush()
        await self.session.refresh(department)
        return department

    async def soft_delete(self, department: Department) -> None:
        department.is_deleted = True
        await self.session.flush()


class TeamRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, team_id: UUID) -> Team | None:
        result = await self.session.execute(
            select(Team)
            .where(Team.id == team_id, Team.is_deleted.is_(False))
            .options(selectinload(Team.department))
        )
        return result.scalar_one_or_none()

    async def list_teams(
        self,
        *,
        department_id: UUID | None = None,
        keyword: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Team], int]:
        stmt = select(Team).where(Team.is_deleted.is_(False)).options(
            selectinload(Team.department)
        )

        if department_id:
            stmt = stmt.where(Team.department_id == department_id)
        if keyword:
            stmt = stmt.where(
                Team.name.ilike(f"%{keyword}%")
                | Team.code.ilike(f"%{keyword}%")
            )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = stmt.order_by(asc(Team.created_at))
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        result = await self.session.execute(stmt)
        return list(result.scalars().all()), total

    async def create(self, team: Team) -> Team:
        self.session.add(team)
        await self.session.flush()
        await self.session.refresh(team)
        return team

    async def update(self, team: Team) -> Team:
        await self.session.flush()
        await self.session.refresh(team)
        return team

    async def soft_delete(self, team: Team) -> None:
        team.is_deleted = True
        await self.session.flush()


class OffboardingRecordRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, record_id: UUID) -> OffboardingRecord | None:
        result = await self.session.execute(
            select(OffboardingRecord)
            .where(OffboardingRecord.id == record_id, OffboardingRecord.is_deleted.is_(False))
            .options(selectinload(OffboardingRecord.employee))
        )
        return result.scalar_one_or_none()

    async def list_records(
        self,
        *,
        employee_id: UUID | None = None,
        keyword: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[OffboardingRecord], int]:
        stmt = (
            select(OffboardingRecord)
            .where(OffboardingRecord.is_deleted.is_(False))
            .options(selectinload(OffboardingRecord.employee))
        )

        if employee_id:
            stmt = stmt.where(OffboardingRecord.employee_id == employee_id)
        if keyword:
            stmt = stmt.join(Employee).where(
                Employee.name.ilike(f"%{keyword}%")
                | Employee.employee_number.ilike(f"%{keyword}%")
            )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = stmt.order_by(desc(OffboardingRecord.created_at))
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        result = await self.session.execute(stmt)
        return list(result.scalars().all()), total

    async def create(self, record: OffboardingRecord) -> OffboardingRecord:
        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)
        return record

    async def update(self, record: OffboardingRecord) -> OffboardingRecord:
        await self.session.flush()
        await self.session.refresh(record)
        return record

    async def soft_delete(self, record: OffboardingRecord) -> None:
        record.is_deleted = True
        await self.session.flush()
