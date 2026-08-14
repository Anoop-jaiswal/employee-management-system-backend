from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.modules.employees.model import Employee


class EmployeeRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(
        self,
        employee_id: UUID,
    ) -> Employee | None:

        statement = select(Employee).where(
            Employee.id == employee_id
        )

        return self.db.scalar(statement)

    def get_by_email(
        self,
        email: str,
    ) -> Employee | None:

        statement = select(Employee).where(
            Employee.email == email
        )

        return self.db.scalar(statement)

    def get_by_employee_code(
        self,
        employee_code: str,
    ) -> Employee | None:

        statement = select(Employee).where(
            Employee.employee_code == employee_code
        )

        return self.db.scalar(statement)

    def create(
        self,
        employee: Employee,
    ) -> Employee:

        self.db.add(employee)
        self.db.flush()

        return employee

    def list(
    self,
    *,
    offset: int,
    limit: int,
    search: str | None = None,
    department: str | None = None,
    is_active: bool | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    ) -> tuple[list[Employee], int]:

        statement = select(Employee)

        if search:
            search_pattern = f"%{search}%"

            statement = statement.where(
                Employee.first_name.ilike(search_pattern)
                | Employee.last_name.ilike(search_pattern)
                | Employee.email.ilike(search_pattern)
                | Employee.employee_code.ilike(search_pattern)
            )

        if department:
            statement = statement.where(
                Employee.department == department
            )

        if is_active is not None:
            statement = statement.where(
                Employee.is_active == is_active
            )

        sort_column = getattr(Employee, sort_by)

        if sort_order == "asc":
            statement = statement.order_by(
                sort_column.asc()
            )
        else:
            statement = statement.order_by(
                sort_column.desc()
            )

        count_statement = select(
            func.count()
        ).select_from(
            statement.subquery()
        )

        total = self.db.scalar(count_statement) or 0

        statement = statement.offset(offset).limit(limit)

        employees = list(
            self.db.scalars(statement).all()
        )

        return employees, total


    def update(
    self,
    employee: Employee,
    values: dict,
    ) -> Employee:

        for field, value in values.items():
            setattr(employee, field, value)

        self.db.flush()

        return employee
    