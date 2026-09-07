from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.media.domain.entities import Media as DomainMedia
from src.core.media.infrastructure.mapper import MediaMapper
from src.core.media.infrastructure.models import Media as ORMMedia


class MediaRepository:
    def __init__(self, session: AsyncSession):
        self._session = session
        self.model = ORMMedia

    async def save(self, media: list[DomainMedia]) -> None:
        mapped_model = MediaMapper.to_orm(media)
        self._session.add_all(mapped_model)
        await self._session.flush()

    async def delete(self, media_id: UUID) -> None:
        statement = delete(self.model).where(self.model.id == media_id)
        await self._session.execute(statement)
        await self._session.flush()

    async def get_by_id(self, media_id: UUID) -> DomainMedia:
        statement = select(self.model).where(self.model.id == media_id)
        result = (await self._session.execute(statement)).scalar_one_or_none()
        if result is None:
            return None

        return MediaMapper.to_domain([result])[0]
