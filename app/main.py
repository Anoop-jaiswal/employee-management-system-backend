from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.core.exception_handlers import (
    app_exception_handler,
    unexpected_exception_handler,
    validation_exception_handler,
)
from app.core.exceptions import AppException
from app.modules.departments.router import router as department_router
from app.modules.employees.router import router as employee_router

app = FastAPI(
    title="Employee Management System",
    version="1.0.0",
)


# -------------------------------------------------------------------
# Exception Handlers
# -------------------------------------------------------------------

app.add_exception_handler(
    AppException,
    app_exception_handler,
)

app.add_exception_handler(
    Exception,
    unexpected_exception_handler,
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)


# -------------------------------------------------------------------
# Health Check
# -------------------------------------------------------------------


@app.get("/health")
def health_check():
    return {"status": "ok"}


# -------------------------------------------------------------------
# API Routers
# -------------------------------------------------------------------

app.include_router(
    department_router,
    prefix="/api/v1",
)

app.include_router(
    employee_router,
    prefix="/api/v1",
)
