from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.modules.departments.schema import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
)
from app.modules.departments.service import (
    DepartmentService,
)

router = APIRouter(
    prefix="/departments",
    tags=["Departments"],
)


@router.post(
    "",
    response_model=DepartmentResponse,
    status_code=201,
)
def create_department(
    data: DepartmentCreate,
    db: Session = Depends(get_db),
):
    service = DepartmentService(db)

    return service.create(data)


@router.patch(
    "/{department_id}",
    response_model=DepartmentResponse,
)
def update_department(
    department_id: UUID,
    data: DepartmentUpdate,
    db: Session = Depends(get_db),
):
    service = DepartmentService(db)

    return service.update(
        department_id,
        data,
    )


@router.get(
    "/{department_id}",
    response_model=DepartmentResponse,
)
def get_department(
    department_id: UUID,
    db: Session = Depends(get_db),
):
    service = DepartmentService(db)

    return service.get_by_id(department_id)
