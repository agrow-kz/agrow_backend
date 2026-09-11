from uuid import UUID

from src.core.admin.domain.enums import AdminRoles
from src.core.shared.presentation.dto import DTO


class CreateAdminRequest(DTO):
    target_email: str
    role: AdminRoles
    last_name: str
    first_name: str
    patronymic: str | None = None


class GrantPermissionRequest(DTO):
    admin_id: UUID
    permission_id: UUID
