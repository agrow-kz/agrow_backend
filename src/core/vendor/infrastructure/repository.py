from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.vendor.domain.entities import Vendor
from src.core.vendor.infrastructure.mapper import VendorMapper
from src.core.vendor.infrastructure.models import Vendor as ORMVendor


class VendorRepository:
    def __init__(self, session: AsyncSession):
        self._session = session
        self.model = ORMVendor

    async def save(self, vendor: Vendor) -> None:
        mapped_model = VendorMapper.to_orm(vendor)
        await self._session.merge(mapped_model)
        await self._session.flush()

    async def get_by_id(self, vendor_id: UUID) -> Vendor:
        statement = select(self.model).where(self.model.id == vendor_id)
        result = (await self._session.execute(statement)).scalar_one_or_none()

        if not result:
            return None
        return VendorMapper.to_domain(result)

    async def get_by_tax_id(self, tax_id: str) -> Vendor:
        statement = select(self.model).where(self.model.tax_id == tax_id)
        result = (await self._session.execute(statement)).scalar_one_or_none()

        if not result:
            return None
        return VendorMapper.to_domain(result)

    async def get_by_account_id(self, account_id: UUID) -> Vendor:
        statement = select(self.model).where(self.model.account_id == account_id)
        result = (await self._session.execute(statement)).scalar_one_or_none()

        if not result:
            return None
        return VendorMapper.to_domain(result)
