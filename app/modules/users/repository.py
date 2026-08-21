from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.users.model import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(
        self,
        email: str,
    ) -> User | None:

        statement = select(User).where(User.email == email)

        return self.db.scalar(statement)

    def create(
        self,
        user: User,
    ) -> User:

        self.db.add(user)

        self.db.flush()

        return user

    def get_by_id(
        self,
        user_id: UUID,
    ) -> User | None:
        statement = select(User).where(User.id == user_id)

        return self.db.scalar(statement)