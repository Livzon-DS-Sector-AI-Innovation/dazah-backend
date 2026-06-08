"""HR module public API for cross-module consumption."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.hr.repository import EmployeeRepository


def _employee_to_dict(emp: Any) -> dict[str, str | None]:
    """Convert an Employee ORM object to a lightweight dict for AI context."""
    return {
        "name": emp.name,
        "employee_number": emp.employee_number,
        "department": emp.department,
        "team": emp.team,
        "position": emp.position,
        "status": emp.status,
        "hire_date": str(emp.hire_date) if emp.hire_date else None,
        "gender": emp.gender,
        "education": emp.education,
        "age": str(emp.age) if emp.age is not None else None,
    }


async def list_employees_by_department(
    session: AsyncSession, department: str
) -> tuple[list[dict[str, str | None]], int]:
    """List employees by department name."""
    repo = EmployeeRepository(session)
    employees, total = await repo.list_employees(department=department, page=1, page_size=200)
    data = [_employee_to_dict(e) for e in employees]
    return data, total


async def query_employees(
    session: AsyncSession,
    *,
    filters: dict[str, Any],
    page: int = 1,
    page_size: int = 200,
) -> tuple[list[dict[str, str | None]], int]:
    """Flexible employee query for AI context injection.

    Args:
        filters: Dict of filter conditions (e.g. {"department": "生产部", "status": "在职"})
        page: Page number (1-based)
        page_size: Items per page

    Returns:
        Tuple of (employee dicts list, total count)
    """
    repo = EmployeeRepository(session)
    employees, total = await repo.list_employees(**filters, page=page, page_size=page_size)
    data = [_employee_to_dict(e) for e in employees]
    return data, total


async def count_employees(
    session: AsyncSession,
    *,
    filters: dict[str, Any],
) -> int:
    """Count employees matching flexible criteria."""
    repo = EmployeeRepository(session)
    _, total = await repo.list_employees(**filters, page=1, page_size=1)
    return total


async def search_employees_by_name(session: AsyncSession, name: str) -> list[dict[str, str | None]]:
    """Search employees by name keyword.

    Returns a lightweight list of employee facts for AI context injection.
    """
    repo = EmployeeRepository(session)
    employees, _ = await repo.list_employees(keyword=name, page=1, page_size=10)
    return [_employee_to_dict(e) for e in employees]


async def search_employees_fuzzy(session: AsyncSession, name: str) -> list[dict[str, str | None]]:
    """Fuzzy search: when exact match returns empty, search by each Chinese character.

    Returns employees whose name contains any character from the query name.
    """
    repo = EmployeeRepository(session)
    seen_ids: set[str] = set()
    results: list[dict[str, str | None]] = []

    for char in name:
        # Only search Chinese characters
        if "一" <= char <= "鿿":
            employees, _ = await repo.list_employees(keyword=char, page=1, page_size=10)
            for e in employees:
                uid = str(e.id)
                if uid not in seen_ids:
                    seen_ids.add(uid)
                    results.append(_employee_to_dict(e))
    return results


async def group_count_employees(
    session: AsyncSession,
    *,
    group_by: str,
    filters: dict[str, Any],
) -> list[dict]:
    """Group employees by a field and count occurrences.

    Args:
        group_by: Field name to group by (e.g. "education", "department")
        filters: Filter conditions

    Returns:
        List of {"value": field_value, "count": int} sorted by count descending.
    """
    repo = EmployeeRepository(session)
    return await repo.group_count(group_by, **filters)


async def get_distinct_employee_values(
    session: AsyncSession,
    *,
    field: str,
    filters: dict[str, Any],
) -> list[str]:
    """Get distinct non-null values for a field.

    Args:
        field: Field name (e.g. "department", "education")
        filters: Filter conditions

    Returns:
        List of distinct values.
    """
    repo = EmployeeRepository(session)
    return await repo.get_distinct_values(field, **filters)
