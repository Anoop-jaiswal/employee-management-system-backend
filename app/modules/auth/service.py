from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import DuplicateResourceException
from app.core.security import hash_password
from app.modules.users.model import User
from app.modules.users.repository import UserRepository
from app.modules.users.schema import UserCreate


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)

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
