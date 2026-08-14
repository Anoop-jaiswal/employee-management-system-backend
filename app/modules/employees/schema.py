from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from typing import Literal

from typing import Generic, TypeVar

T = TypeVar("T")


class EmployeeCreate(BaseModel):
    employee_code: str = Field(min_length=1, max_length=50)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: str = Field(max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    department: str = Field(min_length=1, max_length=100)
    designation: str = Field(min_length=1, max_length=100)
    salary: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    joining_date: date


class EmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    employee_code: str
    first_name: str
    last_name: str
    email: str
    phone: str | None
    department: str
    designation: str
    salary: Decimal
    joining_date: date
    is_active: bool
    created_at: datetime
    updated_at: datetime


class EmployeeListQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    search: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    department: str | None = Field(
        default=None,
        max_length=100,
    )

    is_active: bool | None = None

    sort_by: Literal[
        "created_at",
        "updated_at",
        "joining_date",
        "first_name",
        "employee_code",
    ] = "created_at"

    sort_order: Literal["asc", "desc"] = "desc"


class PaginationMetadata(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int


class EmployeeListResponse(BaseModel):
    items: list[EmployeeResponse]
    pagination: PaginationMetadata


class EmployeeUpdate(BaseModel):
    employee_code: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    first_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    last_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    email: str | None = Field(
        default=None,
        max_length=255,
    )

    phone: str | None = Field(
        default=None,
        max_length=20,
    )

    department: str | None = Field(
        default=None,
        max_length=100,
    )

    designation: str | None = Field(
        default=None,
        max_length=100,
    )

    salary: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=12,
        decimal_places=2,
    )

    joining_date: date | None = None

    is_active: bool | None = None