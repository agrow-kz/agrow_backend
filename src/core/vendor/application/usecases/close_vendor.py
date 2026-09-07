from uuid import UUID

from src.core.customer.application.services.customer_service import CustomerService
from src.core.vendor.domain.entities import Vendor
from src.core.vendor.infrastructure.uow import VendorUnitOfWork


class CloseVendorUseCase:
    def __init__(self, uow: VendorUnitOfWork, customer_service: CustomerService):
        self.uow = uow
        self.customer_service = customer_service

    async def execute(self, vendor_id: UUID):
        async with self.uow as uow:
            vendor: Vendor = await uow.vendor.get_by_id(vendor_id)
            vendor.close()

            await uow.vendor.save(vendor)
            await uow.commit()

        await self.customer_service.create(
            account_id=vendor.account_id,
            last_name=vendor.contact_fullname.contact_last_name,
            first_name=vendor.contact_fullname.contact_first_name,
        )
