import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from src.core.iam.domain.enums import TokenType
from src.core.iam.domain.exceptions import (
    AccountAlreadyConfirmedError,
    AccountNotConfirmedError,
)
from src.core.iam.domain.value_objects import Email, HashedPassword
from src.core.shared.domain.entities import AggregateRoot, Entity


@dataclass(frozen=False)
class Account(AggregateRoot):
    id: UUID
    email: Email
    password: HashedPassword
    password_changed_at: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime | None
    tokens: list["Token"]

    @classmethod
    def create(cls, email: Email, password: HashedPassword) -> "Account":
        return cls(
            id=uuid.uuid4(),
            email=email,
            password=password,
            password_changed_at=datetime.now(timezone.utc),
            is_active=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            tokens=[],
        )

    def confirm_account(self):
        if self.is_active:
            raise AccountAlreadyConfirmedError()
        self.is_active = True

    def resend_confirmation_code(self, token_value: str, expires_at: datetime):
        if self.is_active:
            raise AccountAlreadyConfirmedError()

        self.revoke_all_tokens_by_type(TokenType.EMAIL)
        self.add_new_token(TokenType.EMAIL, token_value, expires_at)

    def login(self):
        if not self.is_active:
            raise AccountNotConfirmedError()

    def logout(self, token_value: str):
        token = self._get_token_by_value(token_value)
        if not token.is_revoked:
            token.revoke_token()

    def add_new_token(self, type: TokenType, value: str, expires_at: datetime):
        new_token = Token.create(self.id, type, value, expires_at)
        self.tokens.append(new_token)
        return new_token

    def rotate_refresh_token(self, old_token: str, new_token: str, expires_at):
        old = self._get_token_by_value(old_token)
        old.revoke_token()
        self.add_new_token(
            type=TokenType.REFRESH, value=new_token, expires_at=expires_at
        )

    def request_reset_password(self, token_value: str, expires_at: datetime):
        self.revoke_all_tokens_by_type(TokenType.PASSWORD)
        self.add_new_token(TokenType.PASSWORD, token_value, expires_at)

    def reset_password(self, new_hashed_password: HashedPassword):
        self.password = new_hashed_password
        self.password_changed_at = datetime.now(timezone.utc)
        self.revoke_all_tokens_by_type(TokenType.REFRESH)

    def revoke_all_tokens_by_type(self, token_type: TokenType):
        for token in self.tokens:
            if token.type == token_type and not token.is_revoked:
                token.revoke_token()

    def change_password(self, new_hashed_password: HashedPassword):
        self.password = new_hashed_password
        self.password_changed_at = datetime.now(timezone.utc)
        self.revoke_all_tokens_by_type(TokenType.REFRESH)

    def change_email(self, new_email: Email):
        self.email = new_email

    def _get_token_by_value(self, token_value: str):
        return next(
            (token for token in self.tokens if token.value == token_value), None
        )


@dataclass(frozen=False)
class Token(Entity):
    id: UUID
    account_id: UUID
    type: TokenType
    value: str
    is_revoked: bool
    expires_at: datetime

    @classmethod
    def create(
        cls, account_id: UUID, type: TokenType, value: str, expires_at: datetime
    ):
        return cls(
            id=uuid.uuid4(),
            account_id=account_id,
            type=type,
            value=value,
            is_revoked=False,
            expires_at=expires_at,
        )

    def revoke_token(self):
        if self.is_revoked:
            raise ValueError("Token is already revoked")
        self.is_revoked = True

    def is_expired(self):
        return self.expires_at < datetime.now(timezone.utc)
