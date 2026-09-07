from loguru import logger

from src.core.iam.infrastructure.uow import IAMUnitOfWork
from src.core.iam.presentation.dto import RefreshData


class LogoutUserUseCase:
    def __init__(self, uow: IAMUnitOfWork):
        self.uow = uow

    async def execute(self, refresh_data: RefreshData):
        async with self.uow as uow:
            account = await uow.account.find_by_token_value(refresh_data.refresh_token)
            if not account:
                return

            account.logout(refresh_data.refresh_token)

            await uow.account.save(account)
            await uow.commit()

        logger.info("Logged out user | account_id={}", account.id)
