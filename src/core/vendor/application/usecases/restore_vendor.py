from uuid import UUID

from src.core.vendor.domain.entities import Vendor
from src.core.vendor.infrastructure.uow import VendorUnitOfWork


class RestoreVendorUseCase:
    def __init__(self, uow: VendorUnitOfWork):
        self.uow = uow

    async def execute(self, account_id: UUID):
        async with self.uow as uow:
            vendor: Vendor = await uow.vendor.get_by_account_id(account_id)
            vendor.restore()

            await uow.vendor.save(vendor)
            await uow.commit()
