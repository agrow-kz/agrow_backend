import pytest

from src.core.admin.domain.enums import AdminRoles
from src.core.admin.domain.exceptions import InsufficientPermissionsError
from src.core.admin.presentation.dto import GrantPermissionRequest
from tests.admin.conftest import create_admin_dto


class TestGrantPermission:
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_successful_grant_permission(
        self,
        admin_service,
        admin_seed,
        prepared_account,
        admin_repository,
        permission_seed,
    ):
        dto = create_admin_dto()
        super_admin = await admin_seed()
        await admin_service.create_admin(super_admin.account_id, dto)

        moderator = await admin_repository.get_by_account_id(prepared_account.id)
        permission = await permission_seed("verify:account")

        grant_dto = GrantPermissionRequest(
            admin_id=moderator.id, permission_id=permission.id
        )
        await admin_service.grant_permission(super_admin.account_id, grant_dto)

        moderator = await admin_repository.get_by_account_id(prepared_account.id)
        moderator_permissions = [p for p in moderator.permissions]
        assert len(moderator_permissions) == 1

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_failed_grant_permission(
        self,
        admin_service,
        admin_seed,
        prepared_account,
        admin_repository,
        permission_seed,
    ):
        dto = create_admin_dto()
        super_admin = await admin_seed()
        await admin_service.create_admin(super_admin.account_id, dto)

        admin = await admin_seed(role=AdminRoles.ADMIN, email="admin2@example.com")

        moderator = await admin_repository.get_by_account_id(prepared_account.id)
        permission = await permission_seed("create:category")
        grant_dto = GrantPermissionRequest(
            admin_id=moderator.id, permission_id=permission.id
        )

        with pytest.raises(InsufficientPermissionsError):
            await admin_service.grant_permission(admin.account_id, grant_dto)

        moderator_permissions = [p for p in moderator.permissions]
        assert len(moderator_permissions) == 0
