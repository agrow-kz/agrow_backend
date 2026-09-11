import uuid
from dataclasses import dataclass, field
from uuid import UUID

from src.core.admin.domain.enums import AdminRoles
from src.core.admin.domain.exceptions import InsufficientPermissionsError
from src.core.shared.domain.entities import AggregateRoot, Entity


@dataclass(frozen=False)
class Admin(AggregateRoot):
    id: UUID
    account_id: UUID
    last_name: str
    first_name: str
    patronymic: str
    role: AdminRoles
    permissions: list["Permission"] = field(default_factory=list)

    @classmethod
    def _create(
        cls,
        account_id: UUID,
        last_name: str,
        first_name: str,
        patronymic: str,
        role: AdminRoles,
    ):
        return cls(
            id=uuid.uuid4(),
            account_id=account_id,
            last_name=last_name,
            first_name=first_name,
            patronymic=patronymic,
            role=role,
        )

    def add_admin(
        self,
        account_id: UUID,
        last_name: str,
        first_name: str,
        patronymic: str,
        role: AdminRoles,
    ) -> "Admin":
        if not self.is_super_admin():
            raise InsufficientPermissionsError()

        return Admin._create(
            account_id=account_id,
            last_name=last_name,
            first_name=first_name,
            patronymic=patronymic,
            role=role,
        )

    def can(self, permission: str) -> bool:
        return self.is_super_admin() or self.has_permission(permission)

    def is_super_admin(self):
        return self.role == AdminRoles.SUPER_ADMIN

    def has_permission(self, permission: str) -> bool:
        return any(p.code == permission for p in self.permissions)

    def grant_permission(self, target: "Admin", permission: "Permission") -> None:
        if not self.is_super_admin():
            raise InsufficientPermissionsError()
        if not any(p.id == permission.id for p in target.permissions):
            target.permissions.append(permission)


@dataclass(frozen=False)
class Permission(Entity):
    id: UUID
    code: str
    description: str
