from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )

class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class SessionResponse(BaseModel):
    id: UUID
    created_at: datetime
    last_active_at: datetime | None
    expires_at: datetime


class SessionListResponse(BaseModel):
    sessions: list[SessionResponse]