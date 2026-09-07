from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.admin.domain.entities import Admin as DomainAdmin
from src.core.admin.infrastructure.mapper import AdminMapper
from src.core.admin.infrastructure.models import Admin as ORMAdmin


class AdminRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, admin: DomainAdmin) -> None:
        mapped_model = AdminMapper.to_orm(admin)
        await self._session.merge(mapped_model)
        await self._session.flush()

    async def get_by_account_id(self, account_id: UUID) -> DomainAdmin | None:
        stmt = select(ORMAdmin).where(ORMAdmin.account_id == account_id)
        result = await self._session.execute(stmt)
        orm_admin = result.scalar_one_or_none()

        if not orm_admin:
            return None

        return AdminMapper.to_domain(orm_admin)

    async def get_by_id(self, admin_id: UUID) -> DomainAdmin | None:
        stmt = select(ORMAdmin).where(ORMAdmin.id == admin_id)
        result = await self._session.execute(stmt)
        orm_admin = result.scalar_one_or_none()

        if not orm_admin:
            return None

        return AdminMapper.to_domain(orm_admin)
