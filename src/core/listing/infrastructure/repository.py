from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.listing.domain.entities import Listing as DomainListing
from src.core.listing.infrastructure.mapper import ListingMapper
from src.core.listing.infrastructure.models import Listing as ORMListing


class ListingRepository:
    def __init__(self, session: AsyncSession):
        self._session = session
        self.model = ORMListing

    async def save(self, listing: DomainListing) -> None:
        mapped_model = ListingMapper.to_orm(listing)
        await self._session.merge(mapped_model)
        await self._session.flush()

    async def get_by_id(self, listing_id: UUID) -> DomainListing:
        statement = select(self.model).where(self.model.id == listing_id)
        query_result = await self._session.execute(statement)
        result = query_result.scalar_one_or_none()

        if result is None:
            return None
        return ListingMapper.to_domain(result)
