from loguru import logger

from src.core.iam.domain.enums import TokenType
from src.core.iam.domain.exceptions import AccountNotFoundError
from src.core.iam.infrastructure.services.pyjwt_token import PyJWTTokenService
from src.core.iam.infrastructure.uow import IAMUnitOfWork
from src.core.iam.presentation.dto import LoginResponse, RefreshData


class RefreshTokenUseCase:
    def __init__(self, uow: IAMUnitOfWork, token_service: PyJWTTokenService):
        self.uow = uow
        self.token_service = token_service

    async def execute(self, refresh_data: RefreshData):
        self.token_service.verify_token(refresh_data.refresh_token, TokenType.REFRESH)
        async with self.uow as uow:
            account = await uow.account.find_by_token_value(refresh_data.refresh_token)
            if not account:
                raise AccountNotFoundError()

            new_access_token = self.token_service.create_token(
                account.id, TokenType.ACCESS
            )
            new_refresh_token = self.token_service.create_token(
                account.id, TokenType.REFRESH
            )

            account.rotate_refresh_token(
                refresh_data.refresh_token,
                new_refresh_token.value,
                new_refresh_token.expires_at,
            )

            await uow.account.save(account)
            await uow.commit()

        logger.info("Token is refreshed | account_id={}", account.id)
        return LoginResponse(
            access_token=new_access_token.value, refresh_token=new_refresh_token.value
        )
