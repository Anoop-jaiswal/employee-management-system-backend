from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.modules.auth.schema import (
    LoginRequest,
    RefreshTokenRequest,
    SessionListResponse,
    TokenResponse,
)
from app.modules.auth.service import AuthService
from app.modules.users.model import User
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


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    return service.login(data)


@router.post(
    "/refresh",
    response_model=TokenResponse,
)
def refresh(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    return service.refresh(data)


@router.post("/logout")
def logout(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    service.logout(data)

    return {
        "message": "Logged out successfully",
    }


@router.get(
    "/sessions",
    response_model=SessionListResponse,
)
def get_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    sessions = service.get_sessions(current_user.id)

    return SessionListResponse(sessions=sessions)


@router.delete(
    "/sessions/{session_id}",
)
def revoke_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    service.revoke_session(
        user_id=current_user.id,
        family_id=session_id,
    )

    return {
        "message": "Session revoked successfully",
    }


@router.post(
    "/logout-all",
)
def logout_all(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    service.logout_all(current_user.id)

    return {
        "message": "Logged out from all sessions",
    }