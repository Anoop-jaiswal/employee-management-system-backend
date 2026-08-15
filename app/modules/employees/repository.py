from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.employees.model import Employee


class EmployeeRepository:
    def __init__(self, db: Session):
        self.db = db

    # ---------------------------------------------------------
    # GET BY ID
    # ---------------------------------------------------------

    def get_by_id(
        self,
        employee_id: UUID,
    ) -> Employee | None:

        statement = select(Employee).where(Employee.id == employee_id)

        return self.db.scalar(statement)

    # ---------------------------------------------------------
    # GET BY EMAIL
    # ---------------------------------------------------------

    def get_by_email(
        self,
        email: str,
    ) -> Employee | None:

        statement = select(Employee).where(Employee.email == email)

        return self.db.scalar(statement)

    # ---------------------------------------------------------
    # GET BY EMPLOYEE CODE
    # ---------------------------------------------------------

    def get_by_employee_code(
        self,
        employee_code: str,
    ) -> Employee | None:

        statement = select(Employee).where(Employee.employee_code == employee_code)

        return self.db.scalar(statement)

    # ---------------------------------------------------------
    # CREATE
    # ---------------------------------------------------------

    def create(
        self,
        employee: Employee,
    ) -> Employee:

        self.db.add(employee)
        self.db.flush()

        return employee

    # ---------------------------------------------------------
    # LIST
    # ---------------------------------------------------------

    def list(
        self,
        *,
        offset: int,
        limit: int,
        search: str | None = None,
        department_id: UUID | None = None,
        is_active: bool | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[Employee], int]:

        statement = select(Employee)

        # Search
        if search:
            search_pattern = f"%{search}%"

            statement = statement.where(
                Employee.first_name.ilike(search_pattern)
                | Employee.last_name.ilike(search_pattern)
                | Employee.email.ilike(search_pattern)
                | Employee.employee_code.ilike(search_pattern)
            )

        # Department filter
        if department_id:
            statement = statement.where(Employee.department_id == department_id)

        # Active filter
        if is_active is not None:
            statement = statement.where(Employee.is_active == is_active)

        # Sorting
        sort_column = getattr(
            Employee,
            sort_by,
        )

        if sort_order == "asc":
            statement = statement.order_by(sort_column.asc())

        else:
            statement = statement.order_by(sort_column.desc())

        # Total count
        count_statement = select(func.count()).select_from(statement.subquery())

        total = self.db.scalar(count_statement) or 0

        # Pagination
        statement = statement.offset(offset).limit(limit)

        employees = list(self.db.scalars(statement).all())

        return employees, total

    # ---------------------------------------------------------
    # UPDATE
    # ---------------------------------------------------------

    def update(
        self,
        employee: Employee,
        values: dict,
    ) -> Employee:

        for field, value in values.items():
            setattr(
                employee,
                field,
                value,
            )

        self.db.flush()

        return employee
