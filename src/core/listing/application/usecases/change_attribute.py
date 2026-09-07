from uuid import UUID

from loguru import logger

from src.core.catalog.infrastructure.attribute_validation import (
    AttributeValidationService,
)
from src.core.listing.domain.exceptions import ListingNotFoundError
from src.core.listing.infrastructure.uow import ListingUnitOfWork
from src.core.listing.presentation.dto import ChangeListingAttributeRequest


class ChangeListingAttributeUseCase:
    def __init__(
        self, uow: ListingUnitOfWork, attribute_validation: AttributeValidationService
    ):
        self.uow = uow
        self.attribute_validation = attribute_validation

    async def execute(
        self, vendor_id: UUID, listing_id: UUID, dto: ChangeListingAttributeRequest
    ):
        validated_attributes = await self.attribute_validation.validate(
            dto.subcategory_id, dto.attributes
        )

        async with self.uow as uow:
            listing = await uow.listing.get_by_id(listing_id)
            if not listing or listing.owner_id != vendor_id:
                raise ListingNotFoundError()

            listing.change_attributes(validated_attributes)
            await uow.listing.save(listing)
            await uow.commit()

        logger.info("Listing attributes changed | listing_id={}", listing.id)
