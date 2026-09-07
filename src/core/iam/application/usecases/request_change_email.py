from uuid import UUID

from loguru import logger

from src.core.iam.application.services.otp import OTPService
from src.core.iam.domain.enums import OTPType
from src.core.iam.domain.exceptions import AccountAlreadyExistsError
from src.core.iam.domain.value_objects import Email
from src.core.iam.infrastructure.uow import IAMUnitOfWork
from src.core.iam.presentation.dto import ChangeEmailRequest
from src.core.shared.infrastructure.services.redis_service import RedisService


class RequestEmailChangeUseCase:
    def __init__(
        self, uow: IAMUnitOfWork, otp_service: OTPService, cache_service: RedisService
    ):
        self.uow = uow
        self.otp_service = otp_service
        self.cache_service = cache_service

    async def execute(self, account_id: UUID, dto: ChangeEmailRequest):
        email_vo = Email(dto.email)
        async with self.uow as uow:
            existing = await uow.account.get_account_by_email(email_vo.value)
            if existing:
                logger.info(
                    "Email change attempt to existing email | account_id={}",
                    existing.id,
                )
                raise AccountAlreadyExistsError()

        await self.cache_service.set(
            key=f"email_change:pending:{account_id}", value=email_vo.value, ttl=300
        )

        await self.otp_service.send(
            account_id=account_id, email=email_vo.value, otp_type=OTPType.CHANGE_EMAIL
        )
