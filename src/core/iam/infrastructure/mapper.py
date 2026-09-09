from src.core.iam.domain.entities import Account as DomainAccount
from src.core.iam.domain.entities import Token as DomainToken
from src.core.iam.domain.value_objects import Email, HashedPassword
from src.core.iam.infrastructure.models import Account as ORMAccount
from src.core.iam.infrastructure.models import Token as ORMToken


class AccountMapper:
    @staticmethod
    def to_orm(account: DomainAccount) -> ORMAccount:
        tokens = TokenMapper.to_orm(account.tokens)
        return ORMAccount(
            id=account.id,
            email=account.email.value,
            password_hash=account.password.value,
            password_changed_at=account.password_changed_at,
            is_active=account.is_active,
            created_at=account.created_at,
            updated_at=account.updated_at,
            tokens=tokens,
        )

    @staticmethod
    def to_domain(account: ORMAccount) -> DomainAccount:
        tokens = TokenMapper.to_domain(account.tokens)
        return DomainAccount(
            id=account.id,
            email=Email(account.email),
            password=HashedPassword(account.password_hash),
            password_changed_at=account.password_changed_at,
            is_active=account.is_active,
            created_at=account.created_at,
            updated_at=account.updated_at,
            tokens=tokens,
        )


class TokenMapper:
    @staticmethod
    def to_orm(tokens: list[DomainToken]) -> list[ORMToken]:
        return [
            ORMToken(
                id=token.id,
                account_id=token.account_id,
                type=token.type,
                value=token.value,
                is_revoked=token.is_revoked,
                expires_at=token.expires_at,
            )
            for token in tokens
        ]

    @staticmethod
    def to_domain(tokens: list[ORMToken]) -> list[DomainToken]:
        return [
            DomainToken(
                id=token.id,
                account_id=token.account_id,
                type=token.type,
                value=token.value,
                is_revoked=token.is_revoked,
                expires_at=token.expires_at,
            )
            for token in tokens
        ]
