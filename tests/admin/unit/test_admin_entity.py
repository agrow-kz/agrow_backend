import uuid

import pytest

from src.core.admin.domain.entities import Permission
from src.core.admin.domain.enums import AdminRoles
from src.core.admin.domain.exceptions import InsufficientPermissionsError
from tests.admin.conftest import create_domain_admin


@pytest.mark.unit
def test_successful_admin_creation():
    super_admin = create_domain_admin()

    new_admin = super_admin.add_admin(
        account_id=uuid.uuid4(),
        last_name="NewAdminLastName",
        first_name="NewAdminFirstName",
        patronymic="NewAdminPatronymic",
        role=AdminRoles.ADMIN,
    )

    assert new_admin.id is not None
    assert new_admin.role == AdminRoles.ADMIN


@pytest.mark.unit
def test_admin_creation_failure():
    admin = create_domain_admin(role=AdminRoles.ADMIN)

    with pytest.raises(InsufficientPermissionsError):
        new_admin = admin.add_admin(
            account_id=uuid.uuid4(),
            last_name="NewAdminLastName",
            first_name="NewAdminFirstName",
            patronymic="NewAdminPatronymic",
            role=AdminRoles.MODERATOR,
        )
        assert new_admin.id is None


@pytest.mark.unit
def test_successful_grant_permission():
    super_admin = create_domain_admin()

    new_admin = super_admin.add_admin(
        account_id=uuid.uuid4(),
        last_name="NewAdminLastName",
        first_name="NewAdminFirstName",
        patronymic="NewAdminPatronymic",
        role=AdminRoles.ADMIN,
    )

    super_admin.grant_permission(
        target=new_admin,
        permission=Permission(
            id=uuid.uuid4(), code="create:admin", description="Grant permission"
        ),
    )

    new_admin_permissions = [p for p in new_admin.permissions]
    assert len(new_admin_permissions) == 1


@pytest.mark.unit
def test_grant_permission_failure():
    admin = create_domain_admin(role=AdminRoles.ADMIN)
    moderator = create_domain_admin(role=AdminRoles.MODERATOR)

    with pytest.raises(InsufficientPermissionsError):
        admin.grant_permission(
            target=moderator,
            permission=Permission(
                id=uuid.uuid4(), code="create:admin", description="Grant permission"
            ),
        )

    moderator_permissions = [p for p in moderator.permissions]
    assert len(moderator_permissions) == 0


@pytest.mark.unit
def test_super_admin_can_do_anything_without_permissions():
    super_admin = create_domain_admin()
    has_access = super_admin.can("something")
    assert has_access is True


@pytest.mark.unit
def test_moderator_can_execute_action():
    super_admin = create_domain_admin()
    moderator = create_domain_admin(role=AdminRoles.MODERATOR)

    super_admin.grant_permission(
        target=moderator,
        permission=Permission(
            id=uuid.uuid4(), code="create:category", description="Granted permission"
        ),
    )

    has_access = moderator.can("create:category")
    assert has_access is True


@pytest.mark.unit
def test_moderator_cannot_execute_action():
    super_admin = create_domain_admin()
    moderator = create_domain_admin(role=AdminRoles.MODERATOR)

    super_admin.grant_permission(
        target=moderator,
        permission=Permission(
            id=uuid.uuid4(), code="create:category", description="Granted permission"
        ),
    )

    has_access = moderator.can("verify:account")
    assert has_access is False
