from dependency_injector import containers, providers

from src.core.admin.application.services.admin_service import AdminService
from src.core.admin.infrastructure.repository import (
    AdminRepository,
    PermissionRepository,
)
from src.core.admin.infrastructure.uow import AdminUnitOfWork


class AdminContainer(containers.DeclarativeContainer):
    session_factory = providers.Dependency()
    database_session = providers.Dependency()
    account_repository = providers.Dependency()

    admin_repository = providers.Factory(
        AdminRepository,
        session=database_session,
    )

    permission_repository = providers.Factory(
        PermissionRepository,
        session=database_session,
    )

    uow = providers.Factory(AdminUnitOfWork, session_factory=session_factory)

    admin_service = providers.Factory(
        AdminService,
        uow=uow,
        account_repository=account_repository,
    )
