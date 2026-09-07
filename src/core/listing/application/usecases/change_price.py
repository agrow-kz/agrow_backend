from uuid import UUID

from loguru import logger

from src.core.listing.application.services.listing_search import ListingSearchService
from src.core.listing.domain.exceptions import ListingNotFoundError
from src.core.listing.infrastructure.uow import ListingUnitOfWork
from src.core.listing.presentation.dto import ChangeListingPriceRequest


class ChangeListingPriceUseCase:
    def __init__(
        self,
        uow: ListingUnitOfWork,
        listing_search_service: ListingSearchService,
    ):
        self.uow = uow
        self.listing_search_service = listing_search_service

    async def execute(
        self, vendor_id: UUID, listing_id: UUID, dto: ChangeListingPriceRequest
    ):
        async with self.uow as uow:
            listing = await uow.listing.get_by_id(listing_id)
            if not listing or listing.owner_id != vendor_id:
                raise ListingNotFoundError()

            listing.change_price(dto.price, dto.currency)
            await uow.listing.save(listing)
            await uow.commit()

        await self.listing_search_service.index_listing(
            listing=listing,
            attributes=listing.attributes,
        )

        logger.info(
            "Listing price changed | listing_id={} new_price={}",
            listing.id,
            listing.price,
        )
