from loguru import logger

from src.core.iam.application.interfaces.password_service import IPasswordService
from src.core.iam.application.services.otp import OTPService
from src.core.iam.domain.entities import Account
from src.core.iam.domain.enums import OTPType
from src.core.iam.domain.exceptions import AccountAlreadyExistsError
from src.core.iam.domain.value_objects import Email, Password
from src.core.iam.infrastructure.uow import IAMUnitOfWork
from src.core.iam.presentation.dto import CreateAccountRequest


class CreateAccountUseCase:
    def __init__(
        self,
        uow: IAMUnitOfWork,
        otp_service: OTPService,
        password_service: IPasswordService,
    ):
        self.uow = uow
        self.otp_service = otp_service
        self.password_service = password_service

    async def execute(self, dto: CreateAccountRequest):
        async with self.uow as uow:
            existing = await uow.account.get_account_by_email(dto.email)
            if existing:
                raise AccountAlreadyExistsError()

            self.password_service.validate(dto.raw_password)
            hashed = self.password_service.hash(dto.raw_password)
            account = Account.create(email=Email(dto.email), password=Password(hashed))

            await uow.account.save(account)
            await uow.commit()

        logger.info("Account created | email={}", dto.email)

        await self.otp_service.send(
            account_id=account.id,
            email=dto.email,
            otp_type=OTPType.CONFIRMATION,
        )

        return account.email.value
