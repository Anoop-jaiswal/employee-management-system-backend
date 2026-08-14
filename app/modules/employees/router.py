from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from fastapi import Query

from app.dependencies.database import get_db
from app.modules.employees.schema import (
    EmployeeCreate,
    EmployeeResponse,
)
from app.modules.employees.service import EmployeeService

from app.modules.employees.schema import (
    EmployeeListQuery,
    EmployeeListResponse,
    EmployeeUpdate
)


router = APIRouter(
    prefix="/employees",
    tags=["Employees"],
)


@router.post(
    "/",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_employee(
    data: EmployeeCreate,
    db: Session = Depends(get_db),
):
    service = EmployeeService(db)

    return service.create_employee(data)

@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse,
)
def get_employee(
    employee_id: UUID,
    db: Session = Depends(get_db),
):
    service = EmployeeService(db)
    return service.get_employee(employee_id)

@router.get(
    "/",
    response_model=EmployeeListResponse,
)
def list_employees(
    query: EmployeeListQuery = Depends(),
    db: Session = Depends(get_db),
):
    service = EmployeeService(db)
    employees, pagination = service.list_employees(
        query
    )
    return EmployeeListResponse(
        items=employees,
        pagination=pagination,
    )


@router.patch(
    "/{employee_id}",
    response_model=EmployeeResponse,
)
def update_employee(
    employee_id: UUID,
    data: EmployeeUpdate,
    db: Session = Depends(get_db),
):
    service = EmployeeService(db)
    return service.update_employee(
        employee_id,
        data,
    )