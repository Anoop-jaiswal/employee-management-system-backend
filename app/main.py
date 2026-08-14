from fastapi import FastAPI

from app.core.exception_handlers import (
    duplicate_resource_handler,
    resource_not_found_handler,
)
from app.core.exceptions import (
    DuplicateResourceException,
    ResourceNotFoundException,
)

from app.modules.employees.router import router as employee_router

app = FastAPI(
    title="Employee Management System",
    version="1.0.0",
)

app.add_exception_handler(
    ResourceNotFoundException,
    resource_not_found_handler,
)

app.add_exception_handler(
    DuplicateResourceException,
    duplicate_resource_handler,
)

app.include_router(
    employee_router,
    prefix="/api/v1",
)

@app.get("/health")
def health_check():
    return {"status": "ok"}