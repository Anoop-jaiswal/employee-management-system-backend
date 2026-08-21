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

    def revoke(
        self,
        refresh_token: RefreshToken,
    ) -> RefreshToken:
        refresh_token.revoked_at = datetime.now(timezone.utc)
        self.db.flush()
        return refresh_token
