from loguru import logger

from src.core.iam.application.services.otp import OTPService
from src.core.iam.domain.enums import OTPType, TokenType
from src.core.iam.domain.exceptions import AccountNotFoundError
from src.core.iam.infrastructure.services.pyjwt_token import PyJWTTokenService
from src.core.iam.infrastructure.uow import IAMUnitOfWork
from src.core.iam.presentation.dto import AccountConfirmation, LoginResponse


class AccountConfirmationUseCase:
    def __init__(
        self,
        uow: IAMUnitOfWork,
        otp_service: OTPService,
        token_service: PyJWTTokenService,
    ):
        self.uow = uow
        self.otp_service = otp_service
        self.token_service = token_service

    async def execute(self, confirmation_data: AccountConfirmation):
        async with self.uow as uow:
            account = await uow.account.get_account_by_email(confirmation_data.email)
            if not account:
                raise AccountNotFoundError()

            await self.otp_service.verify(
                account_id=account.id,
                otp_type=OTPType.CONFIRMATION,
                otp_value=confirmation_data.confirm_code,
            )

            access_token = self.token_service.create_token(account.id, TokenType.ACCESS)
            refresh_token = self.token_service.create_token(
                account.id, TokenType.REFRESH
            )

            account.add_new_token(
                refresh_token.type, refresh_token.value, refresh_token.expires_at
            )

            account.confirm_account()
            await uow.account.save(account)
            await uow.commit()

            logger.info("ACCOUNT VERIFIED | account_id={}", account.id)

            return LoginResponse(
                access_token=access_token.value, refresh_token=refresh_token.value
            )
