from uuid import UUID

from src.core.customer.domain.entities import Customer
from src.core.customer.infrastructure.uow import CustomerUnitOfWork


class CustomerService:
    def __init__(self, uow: CustomerUnitOfWork):
        self.uow = uow

    async def create(self, account_id: UUID, last_name: str, first_name: str):
        async with self.uow as uow:
            existing = await uow.customer.get_by_account_id(account_id)
            if existing:
                return

            customer = Customer.create(
                account_id=account_id,
                last_name=last_name,
                first_name=first_name,
            )

            await uow.customer.save(customer)
            await uow.commit()
