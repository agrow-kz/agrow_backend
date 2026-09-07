import uuid
from datetime import datetime, timedelta, timezone

import jwt

from src.core.iam.domain.enums import TokenType
from src.core.iam.domain.exceptions import (
    InvalidTokenError,
    InvalidTokenTypeError,
    TokenExpiredError,
)
from src.core.iam.presentation.dto import TokenData


class PyJWTTokenService:
    def __init__(
        self,
        secret_key: str,
        algorithm: str,
        access_token_lifetime: timedelta,
        refresh_token_lifetime: timedelta,
    ):
        self._secret_key = secret_key
        self._algorithm = algorithm

        self._lifetimes = {
            TokenType.ACCESS: access_token_lifetime,
            TokenType.REFRESH: refresh_token_lifetime,
        }

    def create_token(self, user_id: uuid.UUID, token_type):
        lifetime = self._lifetimes.get(token_type)
        expires_at = datetime.now(timezone.utc) + lifetime
        payload = {
            "jti": str(uuid.uuid4()),
            "sub": str(user_id),
            "exp": expires_at,
            "token_type": token_type.value,
        }
        token_str = jwt.encode(
            payload=payload, key=self._secret_key, algorithm=self._algorithm
        )

        return TokenData(type=token_type, value=token_str, expires_at=expires_at)

    def verify_token(self, token: str, expected_type: TokenType) -> dict:
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])

            token_type = payload.get("token_type")
            if not token_type or token_type != expected_type.value:
                raise InvalidTokenTypeError()
            return payload

        except jwt.ExpiredSignatureError:
            raise TokenExpiredError()

        except jwt.DecodeError:
            raise InvalidTokenError()
