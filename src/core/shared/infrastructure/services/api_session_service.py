from fastapi import HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials as BearerCredentials

from src.core.iam.presentation.dto import LoginResponse


class APISessionService:
    def __init__(
        self, mode: str, access_token_lifetime: int, refresh_token_lifetime: int
    ):
        self._is_production = mode == "production"
        self._access_token_lifetime = access_token_lifetime * 60
        self._refresh_token_lifetime = refresh_token_lifetime * 24 * 60 * 60

    def extract_token(
        self,
        token_from_bearer: BearerCredentials | None,
        token_from_cookie: str | None,
        client_type: str | None,
    ):
        bearer_token = token_from_bearer.credentials if token_from_bearer else None

        strategies = {
            "web": token_from_cookie,
            "mobile": bearer_token,
            "ios": bearer_token,
            "android": bearer_token,
        }

        token = strategies.get(client_type) or token_from_cookie or bearer_token

        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен авторизации не найден в запросе",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return token

    def prepare_response(
        self, response: Response, tokens: LoginResponse, client_type: str | None
    ) -> LoginResponse | dict:
        if client_type in ("mobile", "ios", "android"):
            return tokens

        self._set_web_cookies(response, tokens)
        return {"status": 200, "message": "Вход выполнен"}

    def _set_web_cookies(self, response: Response, tokens: LoginResponse) -> None:
        response.set_cookie(
            key="access_token",
            value=tokens.access_token,
            httponly=True,
            secure=self._is_production,
            samesite="lax",
            path="/",
            max_age=self._access_token_lifetime,
        )

        response.set_cookie(
            key="refresh_token",
            value=tokens.refresh_token,
            httponly=True,
            secure=self._is_production,
            samesite="lax",
            path="/api/v1/iam",
            max_age=self._refresh_token_lifetime,
        )

    def clear_session(self, response: Response) -> None:
        response.delete_cookie(key="access_token", path="/")
        response.delete_cookie(key="refresh_token", path="/api/v1/iam")
