from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    DuplicateResourceException,
    ResourceNotFoundException,
)

from app.modules.departments.model import Department
from app.modules.departments.repository import (
    DepartmentRepository,
)
from app.modules.departments.schema import (
    DepartmentCreate,
    DepartmentUpdate,
)


class DepartmentService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = DepartmentRepository(db)

    def get_by_id(
        self,
        department_id: UUID,
    ) -> Department:

        department = self.repository.get_by_id(department_id)

        if department is None:
            raise ResourceNotFoundException("Department not found")

        return department

    def create(
        self,
        data: DepartmentCreate,
    ) -> Department:

        existing = self.repository.get_by_code(data.code)

        if existing:
            raise DuplicateResourceException("Department code already exists")

        department = Department(
            name=data.name,
            code=data.code,
            description=data.description,
        )

        try:
            self.repository.create(department)

            self.db.commit()
            self.db.refresh(department)

        except IntegrityError:
            self.db.rollback()

            raise DuplicateResourceException("Department code already exists")

        except Exception:
            self.db.rollback()
            raise

        return department

    def update(
        self,
        department_id: UUID,
        data: DepartmentUpdate,
    ) -> Department:

        department = self.repository.get_by_id(department_id)

        if department is None:
            raise ResourceNotFoundException("Department not found")

        values = data.model_dump(exclude_unset=True)

        if not values:
            return department

        if "code" in values:
            existing = self.repository.get_by_code(values["code"])

            if existing and existing.id != department.id:
                raise DuplicateResourceException("Department code already exists")

        try:
            self.repository.update(
                department,
                values,
            )

            self.db.commit()
            self.db.refresh(department)

        except IntegrityError:
            self.db.rollback()

            raise DuplicateResourceException("Department code already exists")

        except Exception:
            self.db.rollback()
            raise

        return department
