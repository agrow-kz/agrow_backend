from uuid import UUID

from loguru import logger

from src.core.iam.application.services.otp import OTPService
from src.core.iam.domain.enums import OTPType
from src.core.iam.domain.exceptions import (
    AccountNotFoundError,
    EmailChangeRequestNotFoundError,
)
from src.core.iam.domain.value_objects import Email
from src.core.iam.infrastructure.uow import IAMUnitOfWork
from src.core.iam.presentation.dto import ConfirmEmailChangeRequest
from src.core.shared.infrastructure.services.redis_service import RedisService


class ConfirmEmailChangeUseCase:
    def __init__(
        self, uow: IAMUnitOfWork, otp_service: OTPService, cache_service: RedisService
    ):
        self.uow = uow
        self.otp_service = otp_service
        self.cache_service = cache_service

    async def execute(self, account_id: UUID, dto: ConfirmEmailChangeRequest):
        pending_email = await self.cache_service.get(
            f"email_change:pending:{account_id}"
        )
        if not pending_email:
            raise EmailChangeRequestNotFoundError()

        await self.otp_service.verify(
            account_id=account_id, otp_type=OTPType.CHANGE_EMAIL, otp_value=dto.otp_code
        )

        async with self.uow as uow:
            account = await uow.account.get_account_by_id(account_id)
            if not account:
                raise AccountNotFoundError()

            account.change_email(Email(pending_email))
            await uow.account.save(account)
            await uow.commit()

        await self.cache_service.delete(f"email_change:pending:{account_id}")
        logger.info("Email changed | account_id={}", account_id)
