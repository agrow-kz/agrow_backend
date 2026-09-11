from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.configuration.dependencies.container import ApplicationContainer
from src.core.admin.domain.entities import Admin
from src.core.catalog.infrastructure.repositories.attributes import (
    AttributeGroupRepository,
)
from src.core.catalog.presentation.dto.attributes import (
    AttributeGroupResponse,
    CreateAttributeGroupRequest,
)
from src.core.shared.presentation.security import require_admin

attribute_group_router = APIRouter(prefix="/attribute-group")


@attribute_group_router.post("/", response_model=AttributeGroupResponse)
@inject
async def create_attribute_group(
    dto: CreateAttributeGroupRequest,
    repo: Annotated[
        AttributeGroupRepository,
        Depends(Provide[ApplicationContainer.catalog.attribute_group_repository]),
    ],
    current_admin: Admin = Depends(require_admin("create:attribute:group")),
):
    group = await repo.create(key=dto.key, label=dto.label, position=dto.position)
    return group


@attribute_group_router.get("/", response_model=list[AttributeGroupResponse])
@inject
async def get_all_attribute_groups(
    repo: Annotated[
        AttributeGroupRepository,
        Depends(Provide[ApplicationContainer.catalog.attribute_group_repository]),
    ],
):
    return await repo.get_all()
