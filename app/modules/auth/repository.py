from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.auth.model import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        refresh_token: RefreshToken,
    ) -> RefreshToken:

        self.db.add(refresh_token)
        self.db.flush()

        return refresh_token

    def get_by_token_hash(
        self,
        token_hash: str,
    ) -> RefreshToken | None:
        statement = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        return self.db.scalar(statement)

    def revoke_family(
        self,
        family_id: UUID,
    ) -> None:

        statement = select(RefreshToken).where(
            RefreshToken.family_id == family_id,
            RefreshToken.revoked_at.is_(None),
        )

        tokens = self.db.scalars(statement).all()

        now = datetime.now(timezone.utc)

        for token in tokens:
            token.revoked_at = now

        self.db.flush()

    def revoke(
        self,
        refresh_token: RefreshToken,
    ) -> RefreshToken:

        refresh_token.revoked_at = datetime.now(timezone.utc)

        self.db.flush()

        return refresh_token

    def get_by_user_id(
        self,
        user_id: UUID,
    ) -> list[RefreshToken]:

        statement = (
            select(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .order_by(RefreshToken.created_at.desc())
        )

        return list(self.db.scalars(statement).all())

    def get_by_family_id(
        self,
        user_id: UUID,
        family_id: UUID,
    ) -> list[RefreshToken]:

        statement = select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.family_id == family_id,
        )

        return list(self.db.scalars(statement).all())

    def revoke_all_for_user(
        self,
        user_id: UUID,
    ) -> None:

        statement = select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
        )

        tokens = self.db.scalars(statement).all()

        now = datetime.now(timezone.utc)

        for token in tokens:
            token.revoked_at = now

        self.db.flush()