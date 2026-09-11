import uuid
from datetime import datetime, timezone
from uuid import UUID

import pytest

from src.core.admin.domain.entities import Admin
from src.core.admin.domain.enums import AdminRoles
from src.core.admin.presentation.dto import CreateAdminRequest
from src.core.iam.domain.entities import Account
from src.core.iam.domain.value_objects import Email, HashedPassword


def create_domain_admin(
    account_id: UUID | None = None, role: AdminRoles = AdminRoles.SUPER_ADMIN
) -> Admin:
    return Admin(
        id=uuid.uuid4(),
        account_id=account_id or uuid.uuid4(),
        last_name="Test",
        first_name="Test",
        patronymic="Test",
        role=role,
    )


def create_admin_dto():
    return CreateAdminRequest(
        target_email="moderator@example.com",
        role=AdminRoles.MODERATOR,
        last_name="Test",
        first_name="Test",
    )


@pytest.fixture
async def admin_repository(container):
    return await container.admin.admin_repository()


@pytest.fixture(scope="function", autouse=True)
async def prepared_account(account_repository):
    account = Account(
        id=uuid.uuid4(),
        email=Email("moderator@example.com"),
        password=HashedPassword("$2b$12$fakehashstring..."),
        password_changed_at=datetime.now(timezone.utc),
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        tokens=[],
    )

    await account_repository.save(account)
    return account


@pytest.fixture
async def permission_seed(permission_repository):
    async def _get(code: str = "grant:permission"):
        permission = await permission_repository.get_by_code(code)
        assert (
            permission is not None
        ), f"Permission '{code}' not found - проверь permissions.yml/seed"
        return permission

    return _get


@pytest.fixture
async def admin_seed(account_repository, admin_repository):
    async def _create(
        role: AdminRoles = AdminRoles.SUPER_ADMIN,
        email: str = "superadmin@example.com",
    ) -> Admin:
        account = Account(
            id=uuid.uuid4(),
            email=Email(email),
            password=HashedPassword("$2b$12$fakehashstring..."),
            password_changed_at=datetime.now(timezone.utc),
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            tokens=[],
        )
        await account_repository.save(account)

        admin = create_domain_admin(account_id=account.id, role=role)
        await admin_repository.save(admin)

        return admin

    return _create


@pytest.fixture
async def admin_service(container):
    return await container.admin.admin_service()


@pytest.fixture
async def permission_repository(container):
    return await container.admin.permission_repository()
