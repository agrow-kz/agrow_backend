from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter
from fastapi.params import Depends

from src.configuration.dependencies.container import ApplicationContainer
from src.core.admin.application.services.admin_service import AdminService
from src.core.admin.domain.entities import Admin
from src.core.admin.presentation.dto import CreateAdminRequest, GrantPermissionRequest
from src.core.shared.presentation.security import require_admin

admin_router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


@admin_router.post("/")
@inject
async def create_admin(
    dto: CreateAdminRequest,
    service: Annotated[
        AdminService, Depends(Provide[ApplicationContainer.admin.admin_service])
    ],
    current_admin: Admin = Depends(require_admin("create:admin")),
):
    await service.create_admin(current_admin.account_id, dto)
    return {"message": "Администратор успешно создан"}


@admin_router.post("/permission/grant")
@inject
async def grant_permission(
    dto: GrantPermissionRequest,
    service: Annotated[
        AdminService, Depends(Provide[ApplicationContainer.admin.admin_service])
    ],
    current_admin: Admin = Depends(require_admin("grant:permission")),
):
    await service.grant_permission(current_admin.account_id, dto)
    return {"message": "Права для администратора выданы"}
