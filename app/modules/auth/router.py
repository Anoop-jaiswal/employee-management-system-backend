from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.modules.auth.service import AuthService
from app.modules.users.schema import (
    UserCreate,
    UserResponse,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: UserCreate,
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    return service.register(data)
