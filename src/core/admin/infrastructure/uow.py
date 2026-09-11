from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.admin.infrastructure.repository import (
    AdminRepository,
    PermissionRepository,
)
from src.core.shared.infrastructure.sql_alchemy_uow import SQLAlchemyUnitOfWork


class AdminUnitOfWork(SQLAlchemyUnitOfWork):
    def __init__(self, session_factory: Callable[[], AsyncSession]):
        super().__init__(session_factory=session_factory)

    @property
    def admin(self) -> AdminRepository:
        return AdminRepository(self._session)

    @property
    def permission(self) -> PermissionRepository:
        return PermissionRepository(self._session)
