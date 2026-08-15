from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    DuplicateResourceException,
    ResourceNotFoundException,
)


async def resource_not_found_handler(
    request: Request,
    exc: ResourceNotFoundException,
):
    return JSONResponse(
        status_code=404,
        content={
            "detail": exc.message,
        },
    )


async def duplicate_resource_handler(
    request: Request,
    exc: DuplicateResourceException,
):
    return JSONResponse(
        status_code=409,
        content={
            "detail": exc.message,
        },
    )
