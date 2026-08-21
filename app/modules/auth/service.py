from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import (
    DuplicateResourceException,
    InvalidCredentialsException,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.modules.auth.model import RefreshToken
from app.modules.auth.repository import RefreshTokenRepository
from app.modules.auth.schema import (
    LoginRequest,
    RefreshTokenRequest,
    SessionResponse,
    TokenResponse,
)
from app.modules.users.model import User
from app.modules.users.repository import UserRepository
from app.modules.users.schema import UserCreate

family_id = uuid4()

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)
        self.refresh_token_repository = RefreshTokenRepository(db)

    def register(
        self,
        data: UserCreate,
    ) -> User:
        email = data.email.lower()

        existing_user = self.user_repository.get_by_email(email)

        if existing_user:
            raise DuplicateResourceException(
                "Email already registered",
                "EMAIL_ALREADY_REGISTERED",
            )

        user = User(
            email=email,
            password_hash=hash_password(data.password),
        )

        try:
            self.user_repository.create(user)

            self.db.commit()
            self.db.refresh(user)

        except IntegrityError:
            self.db.rollback()

            raise DuplicateResourceException(
                "Email already registered",
                "EMAIL_ALREADY_REGISTERED",
            )

        except Exception:
            self.db.rollback()
            raise

        return user

    def login(
        self,
        data: LoginRequest,
    ) -> TokenResponse:
        email = data.email.lower()

        user = self.user_repository.get_by_email(email)

        if not user:
            raise InvalidCredentialsException()

        password_valid = verify_password(
            data.password,
            user.password_hash,
        )

        if not password_valid:
            raise InvalidCredentialsException()

        if not user.is_active:
            raise InvalidCredentialsException()

        access_token = create_access_token(str(user.id))

        refresh_token = create_refresh_token()

        refresh_token_hash = hash_refresh_token(refresh_token)

        now = datetime.now(timezone.utc)

        refresh_token_record = RefreshToken(
            user_id=user.id,
            family_id=family_id,
            token_hash=refresh_token_hash,
            expires_at=(now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)),
        )

        try:
            self.refresh_token_repository.create(refresh_token_record)

            self.db.commit()

        except Exception:
            self.db.rollback()
            raise

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    def refresh(
        self,
        data: RefreshTokenRequest,
    ) -> TokenResponse:
        token_hash = hash_refresh_token(data.refresh_token)

        stored_token = self.refresh_token_repository.get_by_token_hash(token_hash)

        if stored_token is None:
            raise InvalidCredentialsException()

        now = datetime.now(timezone.utc)

        if stored_token.revoked_at is not None:
            self.refresh_token_repository.revoke_family(stored_token.family_id)
            self.db.commit()
            raise InvalidCredentialsException()

        if stored_token.expires_at <= now:
            raise InvalidCredentialsException()

        user = self.user_repository.get_by_id(stored_token.user_id)

        if user is None:
            raise InvalidCredentialsException()

        if not user.is_active:
            raise InvalidCredentialsException()

        self.refresh_token_repository.revoke(stored_token)

        new_refresh_token = create_refresh_token()

        new_refresh_token_hash = hash_refresh_token(new_refresh_token)

        new_refresh_token_record = RefreshToken(
            id=uuid4(),
            user_id=user.id,
            family_id=stored_token.family_id,
            token_hash=new_refresh_token_hash,
            expires_at=(now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)),
        )

        self.refresh_token_repository.create(new_refresh_token_record)

        new_access_token = create_access_token(str(user.id))

        self.db.commit()

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
        )

    def logout(
        self,
        data: RefreshTokenRequest,
    ) -> None:

        token_hash = hash_refresh_token(data.refresh_token)

        stored_token = self.refresh_token_repository.get_by_token_hash(token_hash)

        if stored_token is None:
            raise InvalidCredentialsException()

        if stored_token.revoked_at is not None:
            raise InvalidCredentialsException()

        try:
            self.refresh_token_repository.revoke(stored_token)

            self.db.commit()

        except Exception:
            self.db.rollback()
            raise

    def get_sessions(
        self,
        user_id: UUID,
    ) -> list[SessionResponse]:

        tokens = self.refresh_token_repository.get_by_user_id(user_id)

        sessions = {}

        for token in tokens:
            family_id = token.family_id

            if family_id not in sessions:
                sessions[family_id] = {
                    "id": family_id,
                    "created_at": token.created_at,
                    "last_active_at": token.created_at,
                    "expires_at": token.expires_at,
                    "revoked": True,
                }

            session = sessions[family_id]

            if token.created_at < session["created_at"]:
                session["created_at"] = token.created_at

            if token.created_at > session["last_active_at"]:
                session["last_active_at"] = token.created_at

            if token.expires_at > session["expires_at"]:
                session["expires_at"] = token.expires_at

            if token.revoked_at is None:
                session["revoked"] = False

        return [
            SessionResponse(
                id=session["id"],
                created_at=session["created_at"],
                last_active_at=session["last_active_at"],
                expires_at=session["expires_at"],
            )
            for session in sessions.values()
            if not session["revoked"]
        ]

    def revoke_session(
        self,
        user_id: UUID,
        family_id: UUID,
    ) -> None:

        tokens = self.refresh_token_repository.get_by_family_id(
            user_id=user_id,
            family_id=family_id,
        )

        if not tokens:
            raise InvalidCredentialsException()

        try:
            self.refresh_token_repository.revoke_family(family_id)

            self.db.commit()

        except Exception:
            self.db.rollback()
            raise

    def logout_all(
        self,
        user_id: UUID,
    ) -> None:

        try:
            self.refresh_token_repository.revoke_all_for_user(user_id)

            self.db.commit()

        except Exception:
            self.db.rollback()
            raise