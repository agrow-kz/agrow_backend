from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from sqlalchemy.exc import IntegrityError

from src.configuration.dependencies.container import ApplicationContainer
from src.core.admin.domain.entities import Admin
from src.core.catalog.infrastructure.exceptions import (
    AttributeAlreadyAttachedError,
    CatalogNotFoundError,
)
from src.core.catalog.infrastructure.repositories.attributes import (
    AttributeDefinitionRepository,
    SubcategoryAttributeRepository,
)
from src.core.catalog.infrastructure.repositories.categories import (
    SubcategoryRepository,
)
from src.core.catalog.presentation.dto.attributes import (
    AttachAttributeRequest,
    SubcategoryAttributeResponse,
)
from src.core.shared.presentation.security import require_admin

subcategory_attribute_router = APIRouter(prefix="/{subcategory_id}/attributes")


@subcategory_attribute_router.post("/", response_model=SubcategoryAttributeResponse)
@inject
async def attach_attribute(
    subcategory_id: UUID,
    dto: AttachAttributeRequest,
    subcategory_repo: Annotated[
        SubcategoryRepository,
        Depends(Provide[ApplicationContainer.catalog.subcategory_repository]),
    ],
    definition_repo: Annotated[
        AttributeDefinitionRepository,
        Depends(Provide[ApplicationContainer.catalog.attribute_definition_repository]),
    ],
    link_repo: Annotated[
        SubcategoryAttributeRepository,
        Depends(Provide[ApplicationContainer.catalog.subcategory_attribute_repository]),
    ],
    current_admin: Admin = Depends(require_admin("create:attribute:link")),
):
    if not await subcategory_repo.get_by_id(subcategory_id):
        raise CatalogNotFoundError(field=str(subcategory_id))
    if not await definition_repo.get_by_id(dto.attribute_id):
        raise CatalogNotFoundError(field=str(dto.attribute_id))

    try:
        link = await link_repo.create(
            subcategory_id=subcategory_id,
            attribute_id=dto.attribute_id,
            group_id=dto.group_id,
            unit_id=dto.unit_id,
            required=dto.required,
            filterable=dto.filterable,
            position=dto.position,
        )
    except IntegrityError:
        raise AttributeAlreadyAttachedError(
            subcategory_id=str(subcategory_id), attribute_id=str(dto.attribute_id)
        )

    return link


@subcategory_attribute_router.delete("/{link_id}")
@inject
async def detach_attribute(
    subcategory_id: UUID,
    link_id: UUID,
    link_repo: Annotated[
        SubcategoryAttributeRepository,
        Depends(Provide[ApplicationContainer.catalog.subcategory_attribute_repository]),
    ],
    current_admin: Admin = Depends(require_admin("delete:attribute:link")),
):
    await link_repo.delete(link_id)
    return {"message": "Attribute detached successfully"}
