from uuid import UUID

from loguru import logger

from src.core.shared.infrastructure.services.phone_normalizer import PhoneNormalizer
from src.core.vendor.domain.entities import Vendor
from src.core.vendor.infrastructure.uow import VendorUnitOfWork
from src.core.vendor.presentation.dto import ChangeContactPhoneRequest


class ChangeContactPhoneUseCase:
    def __init__(self, uow: VendorUnitOfWork, phone_normalizer: PhoneNormalizer):
        self.uow = uow
        self.phone_normalizer = phone_normalizer

    async def execute(self, vendor_id: UUID, dto: ChangeContactPhoneRequest):
        async with self.uow as uow:
            vendor: Vendor = await uow.vendor.get_by_id(vendor_id)
            normalized_phone = self.phone_normalizer.normalize(dto.contact_phone)
            vendor.change_contact_phone(normalized_phone)

            await uow.vendor.save(vendor)
            await uow.commit()

        logger.info(
            "Vendor contact phone changed successfully | vendor_id={}", vendor.id
        )
