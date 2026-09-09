from loguru import logger

from src.core.iam.domain.enums import TokenType
from src.core.iam.domain.exceptions import InvalidLoginCredentialsError
from src.core.iam.infrastructure.services.password_service import PasswordService
from src.core.iam.infrastructure.services.pyjwt_token import PyJWTTokenService
from src.core.iam.infrastructure.uow import IAMUnitOfWork
from src.core.iam.presentation.dto import LoginAccount, LoginResponse


class LoginUserUseCase:
    def __init__(
        self,
        uow: IAMUnitOfWork,
        token_service: PyJWTTokenService,
        password_service: PasswordService,
    ):
        self.uow = uow
        self.token_service = token_service
        self.password_service = password_service

    async def execute(self, login_data: LoginAccount):
        async with self.uow as uow:
            account = await uow.account.get_account_by_email(login_data.email)
            if not account:
                raise InvalidLoginCredentialsError()

            if not self.password_service.verify(
                login_data.raw_password, account.password.value
            ):
                raise InvalidLoginCredentialsError()
            account.login()

            access_token = self.token_service.create_token(account.id, TokenType.ACCESS)
            refresh_token = self.token_service.create_token(
                account.id, TokenType.REFRESH
            )
            account.add_new_token(
                refresh_token.type, refresh_token.value, refresh_token.expires_at
            )

            await uow.account.save(account)
            await uow.commit()

        logger.info("Account logged in | account_id={}", account.id)
        return LoginResponse(
            access_token=access_token.value, refresh_token=refresh_token.value
        )
