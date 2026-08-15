from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.departments.model import Department


class DepartmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(
        self,
        department_id: UUID,
    ) -> Department | None:

        statement = select(Department).where(Department.id == department_id)

        return self.db.scalar(statement)

    def get_by_code(
        self,
        code: str,
    ) -> Department | None:

        statement = select(Department).where(Department.code == code)

        return self.db.scalar(statement)

    def create(
        self,
        department: Department,
    ) -> Department:

        self.db.add(department)
        self.db.flush()

        return department

    def update(
        self,
        department: Department,
        values: dict,
    ) -> Department:

        for field, value in values.items():
            setattr(
                department,
                field,
                value,
            )

        self.db.flush()

        return department
