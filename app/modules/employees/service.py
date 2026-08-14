from uuid import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import DuplicateResourceException
from app.core.exceptions import ResourceNotFoundException
from app.modules.employees.model import Employee
from app.modules.employees.repository import EmployeeRepository
from app.modules.employees.schema import EmployeeCreate, EmployeeUpdate
import math

from app.modules.employees.schema import (
    EmployeeListQuery,
    PaginationMetadata,
)

class EmployeeService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = EmployeeRepository(db)

    def create_employee(
        self,
        data: EmployeeCreate,
    ) -> Employee:

        existing_email = self.repository.get_by_email(
            data.email
        )

        if existing_email:
            raise DuplicateResourceException(
                "Employee with this email already exists"
            )

        existing_code = (
            self.repository.get_by_employee_code(
                data.employee_code
            )
        )

        if existing_code:
            raise DuplicateResourceException(
                "Employee code already exists"
            )

        employee = Employee(
            employee_code=data.employee_code,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            phone=data.phone,
            department=data.department,
            designation=data.designation,
            salary=data.salary,
            joining_date=data.joining_date,
        )

        try:
            self.repository.create(employee)
            self.db.commit()
            self.db.refresh(employee)

        except IntegrityError:
            self.db.rollback()
            raise DuplicateResourceException(
                "Employee with this email or employee code already exists"
            )

        except Exception:
            self.db.rollback()
            raise

        return employee

    def get_employee(
    self,
    employee_id: UUID,
    ) -> Employee:

        employee = self.repository.get_by_id(
            employee_id
        )

        if employee is None:
            raise ResourceNotFoundException(
                "Employee not found"
            )

        return employee


    def list_employees(
    self,
    query: EmployeeListQuery,
    ):
        offset = (
            query.page - 1
        ) * query.page_size

        employees, total = self.repository.list(
            offset=offset,
            limit=query.page_size,
            search=query.search,
            department=query.department,
            is_active=query.is_active,
            sort_by=query.sort_by,
            sort_order=query.sort_order,
        )

        total_pages = (
            math.ceil(total / query.page_size)
            if total > 0
            else 0
        )

        return employees, PaginationMetadata(
            page=query.page,
            page_size=query.page_size,
            total=total,
            total_pages=total_pages,
        )



    def update_employee(
    self,
    employee_id: UUID,
    data: EmployeeUpdate,
    ) -> Employee:

        employee = self.repository.get_by_id(
            employee_id
        )

        if employee is None:
            raise ResourceNotFoundException(
                "Employee not found"
            )

        values = data.model_dump(
            exclude_unset=True
        )

        if not values:
            return employee

        if "email" in values:
            existing = self.repository.get_by_email(
                values["email"]
            )

            if (
                existing is not None
                and existing.id != employee.id
            ):
                raise DuplicateResourceException(
                    "Employee with this email already exists"
                )

        if "employee_code" in values:
            existing = (
                self.repository.get_by_employee_code(
                    values["employee_code"]
                )
            )

            if (
                existing is not None
                and existing.id != employee.id
            ):
                raise DuplicateResourceException(
                    "Employee code already exists"
                )

        try:
            self.repository.update(
                employee,
                values,
            )

            self.db.commit()
            self.db.refresh(employee)

        except IntegrityError:
            self.db.rollback()

            raise DuplicateResourceException(
                "Employee with this email or employee code already exists"
            )

        except Exception:
            self.db.rollback()
            raise

        return employee