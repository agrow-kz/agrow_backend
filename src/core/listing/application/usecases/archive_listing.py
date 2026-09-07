from uuid import UUID

from src.core.listing.domain.exceptions import ListingNotFoundError
from src.core.listing.infrastructure.uow import ListingUnitOfWork


class ArchiveListingUseCase:
    def __init__(self, uow: ListingUnitOfWork):
        self.uow = uow

    async def execute(self, vendor_id: UUID, listing_id: UUID):
        async with self.uow as uow:
            listing = await uow.listing.get_by_id(listing_id)
            if not listing or listing.owner_id != vendor_id:
                raise ListingNotFoundError()

            listing.archive()
            await uow.listing.save(listing)
            await uow.commit()
