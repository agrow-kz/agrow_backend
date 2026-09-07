from uuid import UUID

from loguru import logger

from src.core.vendor.domain.entities import Vendor
from src.core.vendor.infrastructure.uow import VendorUnitOfWork
from src.core.vendor.presentation.dto import ChangeContactFullnameRequest


class ChangeContactFullnameUseCase:
    def __init__(self, uow: VendorUnitOfWork):
        self.uow = uow

    async def execute(self, vendor_id: UUID, dto: ChangeContactFullnameRequest):
        async with self.uow as uow:
            vendor: Vendor = await uow.vendor.get_by_id(vendor_id)
            vendor.change_contact_fullname(
                dto.contact_last_name, dto.contact_first_name, dto.contact_patronymic
            )

            await uow.vendor.save(vendor)
            await uow.commit()

        logger.info(
            "Vendor contact fullname changed successfully | vendor_id={}", vendor.id
        )
