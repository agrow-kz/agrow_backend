from uuid import UUID

from loguru import logger

from src.core.shared.infrastructure.services.redis_service import RedisService
from src.core.vendor.application.services.vendor_validation import (
    TaxpayerValidationService,
)
from src.core.vendor.domain.entities import Vendor
from src.core.vendor.domain.exceptions import VendorAlreadyExistsError
from src.core.vendor.infrastructure.uow import VendorUnitOfWork
from src.core.vendor.presentation.dto import CreateVendorRequest, TaxpayerResponse


class RegisterVendorUseCase:
    def __init__(
        self,
        uow: VendorUnitOfWork,
        cache_service: RedisService,
        taxpayer_validation_service: TaxpayerValidationService,
    ):
        self.uow = uow
        self.cache_service = cache_service
        self.taxpayer_validation_service = taxpayer_validation_service

    async def execute(self, account_id: UUID, dto: CreateVendorRequest):
        cached_taxpayer = await self.cache_service.get(f"taxpayer:{dto.tax_id}")
        if cached_taxpayer:
            taxpayer = TaxpayerResponse.model_validate_json(cached_taxpayer)
        else:
            taxpayer = await self.taxpayer_validation_service.validate(
                dto.tax_id, dto.legal_form
            )

        async with self.uow as uow:
            current_vendor = await uow.vendor.get_by_tax_id(dto.tax_id)
            if current_vendor:
                raise VendorAlreadyExistsError()

            vendor = Vendor.create(
                account_id=account_id,
                contact_last_name=dto.contact_last_name,
                contact_first_name=dto.contact_first_name,
                legal_name=taxpayer.legal_name,
                legal_address=dto.legal_address,
                tax_id=taxpayer.tax_id,
                legal_form=taxpayer.legal_form,
            )

            await uow.vendor.save(vendor)
            await uow.commit()

            logger.info("Vendor registered | vendor_id={}", vendor.id)
