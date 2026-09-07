import uuid
from uuid import UUID

from loguru import logger

from src.core.catalog.infrastructure.attribute_validation import (
    AttributeValidationService,
)
from src.core.listing.application.services.listing_search import ListingSearchService
from src.core.listing.domain.entities import Listing
from src.core.listing.domain.enums import ListingStatus
from src.core.listing.domain.value_objects import Gallery
from src.core.listing.infrastructure.uow import ListingUnitOfWork
from src.core.listing.presentation.dto import CreateListingRequest


class CreateListingUseCase:
    def __init__(
        self,
        uow: ListingUnitOfWork,
        attribute_validation: AttributeValidationService,
        listing_search_service: ListingSearchService,
    ):
        self.uow = uow
        self.attribute_validation = attribute_validation
        self.listing_search_service = listing_search_service

    async def execute(self, owner_id: UUID, dto: CreateListingRequest):
        validated_attributes = await self.attribute_validation.validate(
            dto.subcategory_id, dto.attributes
        )

        async with self.uow as uow:
            listing = Listing(
                id=uuid.uuid4(),
                owner_id=owner_id,
                category_id=dto.category_id,
                subcategory_id=dto.subcategory_id,
                title=dto.title,
                price=dto.price,
                currency=dto.currency,
                city_id=dto.city_id,
                description=dto.description,
                attributes=validated_attributes,
                gallery=Gallery.from_dicts([item.model_dump() for item in dto.gallery]),
                status=ListingStatus.ACTIVE,
            )

            await uow.listing.save(listing)
            await uow.commit()

        await self.listing_search_service.index_listing(
            listing=listing, attributes=listing.attributes
        )

        logger.info("Listing created | listing_id={} owner_id={}", listing.id, owner_id)
        return listing.id
