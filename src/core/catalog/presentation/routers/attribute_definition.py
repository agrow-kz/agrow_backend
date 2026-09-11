from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.configuration.dependencies.container import ApplicationContainer
from src.core.admin.domain.entities import Admin
from src.core.catalog.infrastructure.repositories.attributes import (
    AttributeDefinitionRepository,
)
from src.core.catalog.presentation.dto.attributes import (
    AttributeDefinitionResponse,
    CreateAttributeDefinitionRequest,
)
from src.core.shared.presentation.security import require_admin

attribute_definition_router = APIRouter(prefix="/attribute-definition")


@attribute_definition_router.post("/", response_model=AttributeDefinitionResponse)
@inject
async def create_attribute_definition(
    dto: CreateAttributeDefinitionRequest,
    repo: Annotated[
        AttributeDefinitionRepository,
        Depends(Provide[ApplicationContainer.catalog.attribute_definition_repository]),
    ],
    current_admin: Admin = Depends(require_admin("create:attribute:definition")),
):
    definition = await repo.create(
        key=dto.key,
        label=dto.label,
        type=dto.type,
        options=[opt.model_dump() for opt in dto.options],
        source=dto.source,
    )
    return definition


@attribute_definition_router.get("/", response_model=list[AttributeDefinitionResponse])
@inject
async def get_all_attribute_definitions(
    repo: Annotated[
        AttributeDefinitionRepository,
        Depends(Provide[ApplicationContainer.catalog.attribute_definition_repository]),
    ],
):
    return await repo.get_all()
