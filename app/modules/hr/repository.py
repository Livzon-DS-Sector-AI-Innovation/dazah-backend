"""HR database queries live here."""

from datetime import date
from typing import Any
from uuid import UUID

from sqlalchemy import asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.hr.models import (
    Candidate,
    Department,
    DepartureRecord,
    Employee,
    OffboardingRecord,
    OnboardingRecord,
    Team,
)


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
        team: str | None = None,
        position: str | None = None,
        job_category: str | None = None,
        level: str | None = None,
        gender: str | None = None,
        education: str | None = None,
        political_status: str | None = None,
        marital_status: str | None = None,
        status_category: str | None = None,
        age_min: int | None = None,
        age_max: int | None = None,
        birth_year_min: int | None = None,
        birth_year_max: int | None = None,
        hire_date_after: date | None = None,
        hire_date_before: date | None = None,
        factory_entry_date_after: date | None = None,
        factory_entry_date_before: date | None = None,
        work_start_date_after: date | None = None,
        work_start_date_before: date | None = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[Employee], int]:
        stmt = select(Employee).where(Employee.is_deleted.is_(False))

        if department:
            stmt = stmt.where(Employee.department.ilike(f"{department}%"))
        if status:
            stmt = stmt.where(Employee.status == status)
        else:
            # 默认排除待审批员工，只有显式筛选时才显示
            stmt = stmt.where(Employee.status != "待审批")
        if keyword:
            stmt = stmt.where(
                Employee.name.ilike(f"{keyword}%")
                | Employee.employee_number.ilike(f"{keyword}%")
            )
        if team:
            stmt = stmt.where(Employee.team == team)
        if position:
            stmt = stmt.where(Employee.position.ilike(f"{position}%"))
        if job_category:
            stmt = stmt.where(Employee.job_category == job_category)
        if level:
            stmt = stmt.where(Employee.level == level)
        if gender:
            stmt = stmt.where(Employee.gender == gender)
        if education:
            stmt = stmt.where(Employee.education == education)
        if political_status:
            stmt = stmt.where(Employee.political_status == political_status)
        if marital_status:
            stmt = stmt.where(Employee.marital_status == marital_status)
        if status_category:
            stmt = stmt.where(Employee.status_category == status_category)
        if age_min is not None:
            stmt = stmt.where(Employee.age >= age_min)
        if age_max is not None:
            stmt = stmt.where(Employee.age <= age_max)
        if birth_year_min is not None:
            stmt = stmt.where(Employee.birth_year >= birth_year_min)
        if birth_year_max is not None:
            stmt = stmt.where(Employee.birth_year <= birth_year_max)
        if hire_date_after:
            stmt = stmt.where(Employee.hire_date >= hire_date_after)
        if hire_date_before:
            stmt = stmt.where(Employee.hire_date <= hire_date_before)
        if factory_entry_date_after:
            stmt = stmt.where(Employee.factory_entry_date >= factory_entry_date_after)
        if factory_entry_date_before:
            stmt = stmt.where(Employee.factory_entry_date <= factory_entry_date_before)
        if work_start_date_after:
            stmt = stmt.where(Employee.work_start_date >= work_start_date_after)
        if work_start_date_before:
            stmt = stmt.where(Employee.work_start_date <= work_start_date_before)

        # 并行执行 COUNT 和数据查询，减少 TTFB
        count_stmt = select(func.count()).select_from(stmt.subquery())
        sort_column = getattr(Employee, sort_by, Employee.created_at)
        order_func = desc if sort_order == "desc" else asc
        data_stmt = (
            stmt.order_by(order_func(sort_column))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        # NOTE: asyncio.gather 在共享 AsyncSession 下可能无法真正并行，
        # 且小数据量时顺序执行更稳定。保留顺序执行。
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar() or 0

        data_result = await self.session.execute(data_stmt)
        return list(data_result.scalars().all()), total

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

    def _apply_filters(self, stmt, **filters) -> Any:
        """Apply common filters to a select statement."""
        if filters.get("department"):
            stmt = stmt.where(Employee.department.ilike(f"{filters['department']}%"))
        if filters.get("status"):
            stmt = stmt.where(Employee.status == filters["status"])
        else:
            stmt = stmt.where(Employee.status != "待审批")
        if filters.get("keyword"):
            stmt = stmt.where(
                Employee.name.ilike(f"{filters['keyword']}%")
                | Employee.employee_number.ilike(f"{filters['keyword']}%")
            )
        if filters.get("team"):
            stmt = stmt.where(Employee.team == filters["team"])
        if filters.get("position"):
            stmt = stmt.where(Employee.position.ilike(f"{filters['position']}%"))
        if filters.get("job_category"):
            stmt = stmt.where(Employee.job_category == filters["job_category"])
        if filters.get("level"):
            stmt = stmt.where(Employee.level == filters["level"])
        if filters.get("gender"):
            stmt = stmt.where(Employee.gender == filters["gender"])
        if filters.get("education"):
            stmt = stmt.where(Employee.education == filters["education"])
        if filters.get("political_status"):
            stmt = stmt.where(Employee.political_status == filters["political_status"])
        if filters.get("marital_status"):
            stmt = stmt.where(Employee.marital_status == filters["marital_status"])
        if filters.get("status_category"):
            stmt = stmt.where(Employee.status_category == filters["status_category"])
        if filters.get("age_min") is not None:
            stmt = stmt.where(Employee.age >= filters["age_min"])
        if filters.get("age_max") is not None:
            stmt = stmt.where(Employee.age <= filters["age_max"])
        if filters.get("birth_year_min") is not None:
            stmt = stmt.where(Employee.birth_year >= filters["birth_year_min"])
        if filters.get("birth_year_max") is not None:
            stmt = stmt.where(Employee.birth_year <= filters["birth_year_max"])
        if filters.get("hire_date_after"):
            stmt = stmt.where(Employee.hire_date >= filters["hire_date_after"])
        if filters.get("hire_date_before"):
            stmt = stmt.where(Employee.hire_date <= filters["hire_date_before"])
        if filters.get("factory_entry_date_after"):
            stmt = stmt.where(
                Employee.factory_entry_date >= filters["factory_entry_date_after"]
            )
        if filters.get("factory_entry_date_before"):
            stmt = stmt.where(
                Employee.factory_entry_date <= filters["factory_entry_date_before"]
            )
        if filters.get("work_start_date_after"):
            stmt = stmt.where(
                Employee.work_start_date >= filters["work_start_date_after"]
            )
        if filters.get("work_start_date_before"):
            stmt = stmt.where(
                Employee.work_start_date <= filters["work_start_date_before"]
            )
        return stmt

    async def group_count(self, field_name: str, **filters) -> list[dict]:
        """Group employees by a field and count occurrences.

        Returns:
            List of {"value": field_value, "count": int} sorted by count descending.
        """
        field = getattr(Employee, field_name, None)
        if field is None:
            return []

        stmt = select(field, func.count().label("count")).where(
            Employee.is_deleted.is_(False)
        )
        stmt = self._apply_filters(stmt, **filters)
        stmt = stmt.group_by(field).order_by(desc("count"))
        result = await self.session.execute(stmt)
        rows = result.all()
        return [
            {"value": row[0], "count": row[1]}
            for row in rows
            if row[0] is not None
        ]

    async def get_distinct_values(self, field_name: str, **filters) -> list[str]:
        """Get distinct non-null values for a field.

        Returns:
            List of distinct values.
        """
        field = getattr(Employee, field_name, None)
        if field is None:
            return []

        stmt = select(field).where(Employee.is_deleted.is_(False)).distinct()
        stmt = self._apply_filters(stmt, **filters)
        result = await self.session.execute(stmt)
        rows = result.all()
        return [row[0] for row in rows if row[0] is not None]

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


class OnboardingRecordRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, record_id: UUID) -> OnboardingRecord | None:
        result = await self.session.execute(
            select(OnboardingRecord).where(
                OnboardingRecord.id == record_id,
                OnboardingRecord.is_deleted.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_feishu_record_id(self, feishu_record_id: str) -> OnboardingRecord | None:
        result = await self.session.execute(
            select(OnboardingRecord).where(
                OnboardingRecord.feishu_record_id == feishu_record_id,
                OnboardingRecord.is_deleted.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def list_records(
        self,
        *,
        department: str | None = None,
        position: str | None = None,
        is_employed: str | None = None,
        keyword: str | None = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[OnboardingRecord], int]:
        stmt = select(OnboardingRecord).where(OnboardingRecord.is_deleted.is_(False))

        if department:
            stmt = stmt.where(OnboardingRecord.department == department)
        if position:
            stmt = stmt.where(OnboardingRecord.position.ilike(f"%{position}%"))
        if is_employed:
            stmt = stmt.where(OnboardingRecord.is_employed == is_employed)
        if keyword:
            stmt = stmt.where(
                OnboardingRecord.name.ilike(f"%{keyword}%")
                | OnboardingRecord.employee_number.ilike(f"%{keyword}%")
            )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        sort_column = getattr(OnboardingRecord, sort_by, OnboardingRecord.created_at)
        order_func = desc if sort_order == "desc" else asc
        data_stmt = (
            stmt.order_by(order_func(sort_column))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar() or 0

        data_result = await self.session.execute(data_stmt)
        return list(data_result.scalars().all()), total

    async def create(self, record: OnboardingRecord) -> OnboardingRecord:
        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)
        return record

    async def update(self, record: OnboardingRecord) -> OnboardingRecord:
        await self.session.flush()
        await self.session.refresh(record)
        return record

    async def upsert_by_feishu_record_id(self, data: dict) -> OnboardingRecord:
        """Create or update onboarding record by feishu_record_id (used for Feishu sync)."""
        rid = data.get("feishu_record_id")
        if not rid:
            raise ValueError("feishu_record_id is required for upsert")

        record = await self.get_by_feishu_record_id(rid)
        if record:
            for key, value in data.items():
                if key != "id" and value is not None:
                    setattr(record, key, value)
            await self.session.flush()
            await self.session.refresh(record)
            return record
        else:
            new_record = OnboardingRecord(**{k: v for k, v in data.items() if v is not None})
            self.session.add(new_record)
            await self.session.flush()
            await self.session.refresh(new_record)
            return new_record

    async def count_total(self) -> int:
        result = await self.session.execute(
            select(func.count()).where(OnboardingRecord.is_deleted.is_(False))
        )
        return result.scalar() or 0

    async def count_synced(self) -> int:
        result = await self.session.execute(
            select(func.count()).where(
                OnboardingRecord.is_deleted.is_(False),
                OnboardingRecord.feishu_record_id.isnot(None),
            )
        )
        return result.scalar() or 0

    async def soft_delete(self, record: OnboardingRecord) -> None:
        record.is_deleted = True
        await self.session.flush()


class DepartureRecordRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, record_id: UUID) -> DepartureRecord | None:
        result = await self.session.execute(
            select(DepartureRecord).where(
                DepartureRecord.id == record_id,
                DepartureRecord.is_deleted.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_feishu_record_id(self, feishu_record_id: str) -> DepartureRecord | None:
        result = await self.session.execute(
            select(DepartureRecord).where(
                DepartureRecord.feishu_record_id == feishu_record_id,
                DepartureRecord.is_deleted.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def list_records(
        self,
        *,
        department: str | None = None,
        offboarding_type: str | None = None,
        keyword: str | None = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "offboarding_date",
        sort_order: str = "desc",
    ) -> tuple[list[DepartureRecord], int]:
        stmt = select(DepartureRecord).where(DepartureRecord.is_deleted.is_(False))

        if department:
            stmt = stmt.where(DepartureRecord.department == department)
        if offboarding_type:
            stmt = stmt.where(DepartureRecord.offboarding_type == offboarding_type)
        if keyword:
            stmt = stmt.where(
                DepartureRecord.name.ilike(f"%{keyword}%")
                | DepartureRecord.department.ilike(f"%{keyword}%")
                | DepartureRecord.position.ilike(f"%{keyword}%")
            )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        sort_column = getattr(DepartureRecord, sort_by, DepartureRecord.offboarding_date)
        order_func = desc if sort_order == "desc" else asc
        data_stmt = (
            stmt.order_by(order_func(sort_column))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar() or 0

        data_result = await self.session.execute(data_stmt)
        return list(data_result.scalars().all()), total

    async def create(self, record: DepartureRecord) -> DepartureRecord:
        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)
        return record

    async def update(self, record: DepartureRecord) -> DepartureRecord:
        await self.session.flush()
        await self.session.refresh(record)
        return record

    async def upsert_by_feishu_record_id(self, data: dict) -> DepartureRecord:
        """Create or update departure record by feishu_record_id (used for Feishu sync)."""
        rid = data.get("feishu_record_id")
        if not rid:
            raise ValueError("feishu_record_id is required for upsert")

        record = await self.get_by_feishu_record_id(rid)
        if record:
            for key, value in data.items():
                if key != "id" and value is not None:
                    setattr(record, key, value)
            await self.session.flush()
            await self.session.refresh(record)
            return record
        else:
            new_record = DepartureRecord(**{k: v for k, v in data.items() if v is not None})
            self.session.add(new_record)
            await self.session.flush()
            await self.session.refresh(new_record)
            return new_record

    async def count_total(self) -> int:
        result = await self.session.execute(
            select(func.count()).where(DepartureRecord.is_deleted.is_(False))
        )
        return result.scalar() or 0

    async def count_synced(self) -> int:
        result = await self.session.execute(
            select(func.count()).where(
                DepartureRecord.is_deleted.is_(False),
                DepartureRecord.feishu_record_id.isnot(None),
            )
        )
        return result.scalar() or 0

    async def soft_delete(self, record: DepartureRecord) -> None:
        record.is_deleted = True
        await self.session.flush()


class CandidateRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, candidate_id: UUID) -> Candidate | None:
        result = await self.session.execute(
            select(Candidate).where(Candidate.id == candidate_id, Candidate.is_deleted.is_(False))
        )
        return result.scalar_one_or_none()

    async def get_by_feishu_record_id(self, feishu_record_id: str) -> Candidate | None:
        result = await self.session.execute(
            select(Candidate).where(
                Candidate.feishu_record_id == feishu_record_id,
                Candidate.is_deleted.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def list_candidates(
        self,
        *,
        position: str | None = None,
        education: str | None = None,
        keyword: str | None = None,
        recommendation_level: str | None = None,
        sync_status: str | None = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[Candidate], int]:
        stmt = select(Candidate).where(Candidate.is_deleted.is_(False))

        if position:
            stmt = stmt.where(Candidate.position == position)
        if education:
            stmt = stmt.where(Candidate.education == education)
        if keyword:
            stmt = stmt.where(
                Candidate.name.ilike(f"%{keyword}%")
                | Candidate.position.ilike(f"%{keyword}%")
            )
        if recommendation_level:
            levels = [level.strip() for level in recommendation_level.split(",") if level.strip()]
            print(f"DEBUG REPO: levels={levels}", flush=True)
            if levels:
                stmt = stmt.where(Candidate.recommendation_level.in_(levels))
        if sync_status:
            if sync_status == "unsynced":
                stmt = stmt.where(
                    Candidate.feishu_record_id.is_(None),
                    Candidate.feishu_sync_status.is_(None),
                )
            else:
                stmt = stmt.where(Candidate.feishu_sync_status == sync_status)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        sort_column = getattr(Candidate, sort_by, Candidate.created_at)
        order_func = desc if sort_order == "desc" else asc
        data_stmt = (
            stmt.order_by(order_func(sort_column))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar() or 0

        data_result = await self.session.execute(data_stmt)
        return list(data_result.scalars().all()), total

    async def create(self, candidate: Candidate) -> Candidate:
        self.session.add(candidate)
        await self.session.flush()
        await self.session.refresh(candidate)
        return candidate

    async def update(self, candidate: Candidate) -> Candidate:
        await self.session.flush()
        await self.session.refresh(candidate)
        return candidate

    async def upsert_by_feishu_record_id(self, data: dict) -> Candidate:
        """Create or update candidate by feishu_record_id (used for Feishu sync)."""
        rid = data.get("feishu_record_id")
        if not rid:
            raise ValueError("feishu_record_id is required for upsert")

        candidate = await self.get_by_feishu_record_id(rid)
        if candidate:
            for key, value in data.items():
                if key != "id" and value is not None:
                    setattr(candidate, key, value)
            await self.session.flush()
            await self.session.refresh(candidate)
            return candidate
        else:
            new_candidate = Candidate(**{k: v for k, v in data.items() if v is not None})
            self.session.add(new_candidate)
            await self.session.flush()
            await self.session.refresh(new_candidate)
            return new_candidate

    async def count_total(self) -> int:
        result = await self.session.execute(
            select(func.count()).where(Candidate.is_deleted.is_(False))
        )
        return result.scalar() or 0

    async def count_synced(self) -> int:
        result = await self.session.execute(
            select(func.count()).where(
                Candidate.is_deleted.is_(False),
                Candidate.feishu_record_id.isnot(None),
            )
        )
        return result.scalar() or 0

    async def count_failed_sync(self) -> int:
        result = await self.session.execute(
            select(func.count()).where(
                Candidate.is_deleted.is_(False),
                Candidate.feishu_sync_status == "failed",
            )
        )
        return result.scalar() or 0

    async def count_pending_sync(self) -> int:
        result = await self.session.execute(
            select(func.count()).where(
                Candidate.is_deleted.is_(False),
                Candidate.feishu_record_id.is_(None),
                Candidate.feishu_sync_status.is_(None),
            )
        )
        return result.scalar() or 0

    async def soft_delete(self, candidate: Candidate) -> None:
        candidate.is_deleted = True
        await self.session.flush()
