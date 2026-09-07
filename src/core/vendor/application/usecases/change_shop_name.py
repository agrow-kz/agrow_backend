from uuid import UUID

from loguru import logger

from src.core.vendor.domain.entities import Vendor
from src.core.vendor.infrastructure.uow import VendorUnitOfWork
from src.core.vendor.presentation.dto import ChangeShopNameRequest


class ChangeShopNameUseCase:
    def __init__(self, uow: VendorUnitOfWork):
        self.uow = uow

    async def execute(self, vendor_id: UUID, dto: ChangeShopNameRequest):
        async with self.uow as uow:
            vendor: Vendor = await uow.vendor.get_by_id(vendor_id)
            vendor.change_shop_name(dto.shop_name)

            await uow.vendor.save(vendor)
            await uow.commit()

        logger.info(
            "Vendor shop name changed successfully | vendor_id={} shop_name={}",
            vendor.id,
            vendor.shop_name,
        )
