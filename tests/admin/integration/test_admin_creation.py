import pytest

from src.core.admin.domain.enums import AdminRoles
from src.core.admin.domain.exceptions import InsufficientPermissionsError
from tests.admin.conftest import create_admin_dto


class TestAdminCreation:
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_successful_admin_creation(
        self,
        admin_service,
        admin_seed,
        prepared_account,
        admin_repository,
    ):
        dto = create_admin_dto()
        super_admin = await admin_seed()
        await admin_service.create_admin(super_admin.account_id, dto)

        moderator = await admin_repository.get_by_account_id(prepared_account.id)
        assert moderator is not None
        assert moderator.role == AdminRoles.MODERATOR

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_failed_admin_creation(
        self,
        admin_service,
        admin_seed,
        prepared_account,
        admin_repository,
    ):
        dto = create_admin_dto()
        admin = await admin_seed(role=AdminRoles.ADMIN)

        with pytest.raises(InsufficientPermissionsError):
            await admin_service.create_admin(admin.account_id, dto)

        moderator = await admin_repository.get_by_account_id(prepared_account.id)
        assert moderator is None
