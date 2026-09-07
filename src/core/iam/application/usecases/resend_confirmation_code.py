from loguru import logger

from src.core.iam.application.services.otp import OTPService
from src.core.iam.domain.enums import OTPType
from src.core.iam.infrastructure.uow import IAMUnitOfWork
from src.core.iam.presentation.dto import ResendCodeRequest


class ResendConfirmationCodeUseCase:
    def __init__(
        self,
        uow: IAMUnitOfWork,
        otp_service: OTPService,
    ):
        self.uow = uow
        self.otp_service = otp_service

    async def execute(self, resend_data: ResendCodeRequest):
        async with self.uow as uow:
            account = await uow.account.get_account_by_email(resend_data.email)
            if not account:
                logger.info("Account not found | email={}", resend_data.email)
                return

        await self.otp_service.send(
            account_id=account.id,
            email=account.email.value,
            otp_type=OTPType.CONFIRMATION,
        )
