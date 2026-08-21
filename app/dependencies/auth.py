from uuid import UUID

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import InvalidCredentialsException
from app.dependencies.database import get_db
from app.modules.users.model import User
from app.modules.users.repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except InvalidTokenError:
        raise InvalidCredentialsException()

    user_id = payload.get("sub")

    if not user_id:
        raise InvalidCredentialsException()

    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise InvalidCredentialsException()

    repository = UserRepository(db)

    user = repository.get_by_id(user_uuid)

    if not user:
        raise InvalidCredentialsException()

    if not user.is_active:
        raise InvalidCredentialsException()

    return user
