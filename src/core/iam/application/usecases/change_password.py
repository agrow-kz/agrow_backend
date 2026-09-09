from uuid import UUID

from src.core.iam.domain.exceptions import PasswordMismatchError
from src.core.iam.infrastructure.services.password_service import PasswordService
from src.core.iam.infrastructure.uow import IAMUnitOfWork
from src.core.iam.presentation.dto import ChangePasswordData


class ChangePasswordUseCase:
    def __init__(self, uow: IAMUnitOfWork, password_service: PasswordService):
        self.uow = uow
        self.password_service = password_service

    async def execute(self, account_id: UUID, change_password_data: ChangePasswordData):
        async with self.uow as uow:
            account = await uow.account.get_account_by_id(account_id)

            validated_plain = self.password_service.validate(
                change_password_data.new_password
            )
            if not self.password_service.verify(
                change_password_data.raw_password, account.password.value
            ):
                raise PasswordMismatchError()

            new_hashed_password = self.password_service.hash(validated_plain)
            account.change_password(new_hashed_password)

            await uow.account.save(account)
            await uow.commit()
