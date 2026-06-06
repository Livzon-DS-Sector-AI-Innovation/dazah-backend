"""HR module public API for cross-module consumption."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.hr.repository import EmployeeRepository


async def search_employees_by_name(session: AsyncSession, name: str) -> list[dict[str, str | None]]:
    """Search employees by name keyword.

    Returns a lightweight list of employee facts for AI context injection.
    """
    repo = EmployeeRepository(session)
    employees, _ = await repo.list_employees(keyword=name, page=1, page_size=10)
    return [
        {
            "name": e.name,
            "employee_number": e.employee_number,
            "department": e.department,
            "team": e.team,
            "position": e.position,
            "status": e.status,
            "hire_date": str(e.hire_date) if e.hire_date else None,
        }
        for e in employees
    ]


async def search_employees_fuzzy(session: AsyncSession, name: str) -> list[dict[str, str | None]]:
    """Fuzzy search: when exact match returns empty, search by each Chinese character.

    Returns employees whose name contains any character from the query name.
    """
    repo = EmployeeRepository(session)
    seen_ids: set[str] = set()
    results: list[dict[str, str | None]] = []

    for char in name:
        # Only search Chinese characters
        if '一' <= char <= '鿿':
            employees, _ = await repo.list_employees(keyword=char, page=1, page_size=10)
            for e in employees:
                uid = str(e.id)
                if uid not in seen_ids:
                    seen_ids.add(uid)
                    results.append(
                        {
                            "name": e.name,
                            "employee_number": e.employee_number,
                            "department": e.department,
                            "team": e.team,
                            "position": e.position,
                            "status": e.status,
                            "hire_date": str(e.hire_date) if e.hire_date else None,
                        }
                    )
    return results


async def list_employees_by_department(
    session: AsyncSession, department: str
) -> tuple[list[dict[str, str | None]], int]:
    """List all employees in a given department."""
    repo = EmployeeRepository(session)
    employees, total = await repo.list_employees(
        department=department, page=1, page_size=200
    )
    data = [
        {
            "name": e.name,
            "employee_number": e.employee_number,
            "department": e.department,
            "team": e.team,
            "position": e.position,
            "status": e.status,
            "hire_date": str(e.hire_date) if e.hire_date else None,
        }
        for e in employees
    ]
    return data, total


async def count_employees(
    session: AsyncSession,
    department: str | None = None,
    status: str | None = None,
) -> int:
    """Count employees matching criteria."""
    repo = EmployeeRepository(session)
    _, total = await repo.list_employees(
        department=department, status=status, page=1, page_size=1
    )
    return total
