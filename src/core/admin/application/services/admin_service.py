from uuid import UUID

from src.core.admin.domain.exceptions import (
    AdminAlreadyExistsError,
    AdminNotFoundError,
    PermissionNotFoundError,
)
from src.core.admin.infrastructure.uow import AdminUnitOfWork
from src.core.admin.presentation.dto import CreateAdminRequest, GrantPermissionRequest
from src.core.iam.domain.exceptions import AccountNotFoundError
from src.core.iam.infrastructure.repository import AccountRepository


class AdminService:
    def __init__(self, uow: AdminUnitOfWork, account_repository: AccountRepository):
        self.uow = uow
        self.account_repository = account_repository

    async def create_admin(self, account_id: UUID, dto: CreateAdminRequest) -> None:
        target_account = await self.account_repository.get_account_by_email(
            dto.target_email
        )
        if not target_account:
            raise AccountNotFoundError()

        async with self.uow as uow:
            initiator = await uow.admin.get_by_account_id(account_id)
            if not initiator:
                raise AdminNotFoundError()

            existing = await uow.admin.get_by_account_id(target_account.id)
            if existing:
                raise AdminAlreadyExistsError()

            admin = initiator.add_admin(
                account_id=target_account.id,
                last_name=dto.last_name,
                first_name=dto.first_name,
                patronymic=dto.patronymic,
                role=dto.role,
            )

            await uow.admin.save(admin)
            await uow.commit()

    async def grant_permission(
        self, initiator_account_id: UUID, dto: GrantPermissionRequest
    ) -> None:
        async with self.uow as uow:
            initiator = await uow.admin.get_by_account_id(initiator_account_id)
            if not initiator:
                raise AdminNotFoundError()

            permission = await uow.permission.get_by_id(dto.permission_id)
            if not permission:
                raise PermissionNotFoundError()

            target_admin = await uow.admin.get_by_id(dto.admin_id)
            if not target_admin:
                raise AdminNotFoundError()

            initiator.grant_permission(target_admin, permission)
            await uow.admin.save(target_admin)
            await uow.commit()
