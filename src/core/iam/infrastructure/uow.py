from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.iam.infrastructure.repository import AccountRepository
from src.core.shared.infrastructure.sql_alchemy_uow import SQLAlchemyUnitOfWork


class IAMUnitOfWork(SQLAlchemyUnitOfWork):
    def __init__(self, session_factory: Callable[[], AsyncSession]):
        super().__init__(session_factory=session_factory)

    @property
    def account(self) -> AccountRepository:
        if self._session is None:
            raise RuntimeError("UoW not initialized!")
        return AccountRepository(self._session)
