from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.customer.domain.entities import Customer as DomainCustomer
from src.core.customer.infrastructure.mapper import CustomerMapper
from src.core.customer.infrastructure.models import Customer as ORMCustomer


class CustomerRepository:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._model = ORMCustomer

    async def save(self, buyer: DomainCustomer) -> None:
        mapped_model = CustomerMapper.to_orm(buyer)
        await self._session.merge(mapped_model)
        await self._session.flush()

    async def get_by_id(self, customer_id: UUID) -> DomainCustomer:
        statement = select(self._model).where(self._model.id == customer_id)

        result = (await self._session.execute(statement)).scalar_one_or_none()
        if result is None:
            return None
        return CustomerMapper.to_domain(result)

    async def get_by_account_id(self, account_id: UUID) -> DomainCustomer:
        statement = select(self._model).where(self._model.account_id == account_id)

        query_result = await self._session.execute(statement)
        orm_model = query_result.scalar_one_or_none()

        if orm_model is None:
            return None

        return CustomerMapper.to_domain(orm_model)
