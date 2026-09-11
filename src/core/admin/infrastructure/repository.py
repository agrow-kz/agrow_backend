from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.admin.domain.entities import Admin as DomainAdmin
from src.core.admin.domain.entities import Permission as DomainPermission
from src.core.admin.infrastructure.mapper import AdminMapper, PermissionMapper
from src.core.admin.infrastructure.models import Admin as ORMAdmin
from src.core.admin.infrastructure.models import Permission as ORMPermission


class AdminRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, admin: DomainAdmin) -> None:
        orm_admin = await self._session.get(ORMAdmin, admin.id)

        if orm_admin is None:
            orm_admin = AdminMapper.to_orm(admin)
            self._session.add(orm_admin)
        else:
            orm_admin.last_name = admin.last_name
            orm_admin.first_name = admin.first_name
            orm_admin.patronymic = admin.patronymic
            orm_admin.role = admin.role.value

        if admin.permissions:
            permission_ids = [p.id for p in admin.permissions]
            stmt = select(ORMPermission).where(ORMPermission.id.in_(permission_ids))
            result = await self._session.execute(stmt)
            orm_admin.permissions = list(result.scalars().all())
        else:
            orm_admin.permissions = []

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


class PermissionRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, permission_id: UUID) -> DomainPermission | None:
        stmt = select(ORMPermission).where(ORMPermission.id == permission_id)
        query_result = await self._session.execute(stmt)
        result = query_result.scalar_one_or_none()

        if not result:
            return None
        return PermissionMapper.to_domain(result)

    async def get_by_code(self, code: str) -> DomainPermission | None:
        stmt = select(ORMPermission).where(ORMPermission.codename == code)
        result = await self._session.execute(stmt)
        orm_permission = result.scalar_one_or_none()

        if not orm_permission:
            return None
        return PermissionMapper.to_domain(orm_permission)
