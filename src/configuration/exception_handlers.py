# src/configuration/exception_handlers.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger

from src.core.shared.domain.exceptions import (
    AccessDeniedError,
    AlreadyExistsError,
    NotFoundError,
    RulesError,
    UnauthorizedError,
    ValidationError,
)


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Регистрируем хэндлеры на базовые классы исключений.
    Любой наследник автоматически попадает в нужный хэндлер:
    AccountNotFoundError -> NotFoundError -> 404
    InvalidCredentialsError -> UnauthorizedError -> 401
    и т.д.
    """

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        # 404 — сущность не найдена
        logger.warning(
            "NotFoundError | {} {} | {}", request.method, request.url.path, exc.message
        )
        return JSONResponse(status_code=404, content={"detail": exc.message})

    @app.exception_handler(AlreadyExistsError)
    async def already_exists_handler(request: Request, exc: AlreadyExistsError):
        # 409 Conflict — сущность уже существует
        logger.warning(
            "AlreadyExistsError | {} {} | {}",
            request.method,
            request.url.path,
            exc.message,
        )
        return JSONResponse(status_code=409, content={"detail": exc.message})

    @app.exception_handler(UnauthorizedError)
    async def unauthorized_handler(request: Request, exc: UnauthorizedError):
        # 401 — не аутентифицирован, невалидный токен, неверные креды
        logger.warning(
            "UnauthorizedError | {} {} | {}",
            request.method,
            request.url.path,
            exc.message,
        )
        return JSONResponse(status_code=401, content={"detail": exc.message})

    @app.exception_handler(ValidationError)
    async def validation_handler(request: Request, exc: ValidationError):
        # 422 — невалидные данные по формату (email, пароль, имя)
        logger.warning(
            "ValidationError | {} {} | {}",
            request.method,
            request.url.path,
            exc.message,
        )
        return JSONResponse(status_code=422, content={"detail": exc.message})

    @app.exception_handler(RulesError)
    async def rules_handler(request: Request, exc: RulesError):
        # 400 — данные валидны, но нарушено бизнес-правило
        # OTP cooldown, неверный OTP код, компания на ликвидации и т.д.
        logger.warning(
            "RulesError | {} {} | {}", request.method, request.url.path, exc.message
        )
        return JSONResponse(status_code=400, content={"detail": exc.message})

    @app.exception_handler(AccessDeniedError)
    async def access_denied_error(request: Request, exc: AccessDeniedError):
        logger.warning(
            "AccessDeniedError | {} {} | {}",
            request.method,
            request.url.path,
            exc.message,
        )
        return JSONResponse(
            status_code=403, content={"detail": "Недостаточно прав доступа"}
        )

    @app.exception_handler(Exception)
    async def unexpected_error_handler(request: Request, exc: Exception):
        # 500 — всё что не поймали выше
        # logger.exception автоматически пишет полный traceback
        logger.exception("Unexpected error | {} {}", request.method, request.url.path)
        return JSONResponse(
            status_code=500, content={"detail": "Внутренняя ошибка сервера"}
        )
