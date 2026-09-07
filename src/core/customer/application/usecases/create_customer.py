from uuid import UUID

from loguru import logger

from src.core.customer.domain.entities import Customer
from src.core.customer.infrastructure.uow import CustomerUnitOfWork
from src.core.customer.presentation.dto import CreateCustomerRequest


class CreateCustomerUseCase:
    def __init__(self, uow: CustomerUnitOfWork):
        self.uow = uow

    async def execute(self, account_id: UUID, dto: CreateCustomerRequest):
        async with self.uow as uow:
            new_customer = Customer.create(
                account_id=account_id,
                last_name=dto.last_name,
                first_name=dto.first_name,
            )

            await uow.customer.save(new_customer)
            await uow.commit()

        logger.info("Customer created | customer_id={}", new_customer.id)
