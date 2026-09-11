from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.configuration.dependencies.container import ApplicationContainer
from src.core.admin.domain.entities import Admin
from src.core.catalog.infrastructure.enums import CatalogStatus
from src.core.catalog.infrastructure.exceptions import CatalogNotFoundError
from src.core.catalog.infrastructure.repositories.categories import (
    CategoryRepository,
    SubcategoryRepository,
)
from src.core.catalog.presentation.dto.subcategory import (
    ChangeSubcategoryNameRequest,
    ChangeSubcategoryParentRequest,
    CreateSubcategoryRequest,
)
from src.core.shared.presentation.security import require_admin

subcategory_router = APIRouter(prefix="/subcategory")


@subcategory_router.post("/", summary="Create a new subcategory")
@inject
async def create_subcategory(
    dto: CreateSubcategoryRequest,
    subcategory_repo: Annotated[
        SubcategoryRepository,
        Depends(Provide[ApplicationContainer.catalog.subcategory_repository]),
    ],
    category_repo: Annotated[
        CategoryRepository,
        Depends(Provide[ApplicationContainer.catalog.category_repository]),
    ],
    current_admin: Admin = Depends(require_admin("create:subcategory")),
):
    category = await category_repo.get_by_id(dto.category_id)
    if not category:
        raise CatalogNotFoundError(field=str(dto.category_id))

    subcategory = await subcategory_repo.create(
        category_id=dto.category_id, name=dto.name
    )
    return {"message": "Subcategory created successfully", "id": subcategory.id}


@subcategory_router.patch("/{subcategory_id}/parent")
@inject
async def change_subcategory_parent(
    subcategory_id: UUID,
    dto: ChangeSubcategoryParentRequest,
    subcategory_repo: Annotated[
        SubcategoryRepository,
        Depends(Provide[ApplicationContainer.catalog.subcategory_repository]),
    ],
    category_repo: Annotated[
        CategoryRepository,
        Depends(Provide[ApplicationContainer.catalog.category_repository]),
    ],
    current_admin: Admin = Depends(require_admin("update:subcategory")),
):
    category = await category_repo.get_by_id(dto.category_id)
    if not category:
        raise CatalogNotFoundError(field=str(dto.category_id))

    subcategory = await subcategory_repo.get_by_id(subcategory_id)
    if not subcategory:
        raise CatalogNotFoundError(field=str(subcategory_id))

    subcategory.category_id = dto.category_id
    await subcategory_repo.save(subcategory)
    return {"message": "Subcategory parent updated successfully"}


@subcategory_router.patch("/{subcategory_id}/name")
@inject
async def change_subcategory_name(
    subcategory_id: UUID,
    dto: ChangeSubcategoryNameRequest,
    subcategory_repo: Annotated[
        SubcategoryRepository,
        Depends(Provide[ApplicationContainer.catalog.subcategory_repository]),
    ],
    current_admin: Admin = Depends(require_admin("update:subcategory")),
):
    subcategory = await subcategory_repo.get_by_id(subcategory_id)
    if not subcategory:
        raise CatalogNotFoundError(field=str(subcategory_id))

    subcategory.name = dto.name
    await subcategory_repo.save(subcategory)
    return {"message": "Subcategory name updated successfully"}


@subcategory_router.delete("/{subcategory_id}")
@inject
async def delete_subcategory(
    subcategory_id: UUID,
    subcategory_repo: Annotated[
        SubcategoryRepository,
        Depends(Provide[ApplicationContainer.catalog.subcategory_repository]),
    ],
    current_admin: Admin = Depends(require_admin("delete:subcategory")),
):
    subcategory = await subcategory_repo.get_by_id(subcategory_id)
    if not subcategory:
        raise CatalogNotFoundError(field=str(subcategory_id))

    subcategory.status = CatalogStatus.DELETED
    await subcategory_repo.save(subcategory)
    return {"message": "Subcategory deleted successfully"}
