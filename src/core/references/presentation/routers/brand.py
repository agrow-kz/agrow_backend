from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends

from src.configuration.dependencies.container import ApplicationContainer
from src.core.admin.domain.entities import Admin
from src.core.references.infrastructure.repositories.brand import BrandRepository
from src.core.references.presentation.dto.brand import (
    BrandResponse,
    CreateBrandRequest,
    UpdateBrandRequest,
)
from src.core.shared.presentation.security import require_admin

brand_router = APIRouter(prefix="/brand")


@inject
async def get_repo(
    repo: Annotated[
        BrandRepository,
        Depends(Provide[ApplicationContainer.reference.brand_repository]),
    ],
) -> BrandRepository:
    return repo


@brand_router.get("/", response_model=list[BrandResponse])
async def get_all(repo: BrandRepository = Depends(get_repo)):
    return await repo.get_all()


@brand_router.get("/{brand_id}", response_model=BrandResponse)
async def get_by_id(brand_id: UUID, repo: BrandRepository = Depends(get_repo)):
    brand = await repo.get_by_id(brand_id)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Бренд не найден"
        )
    return brand


@brand_router.post(
    "/", response_model=BrandResponse, status_code=status.HTTP_201_CREATED
)
async def create(
    dto: CreateBrandRequest,
    repo: BrandRepository = Depends(get_repo),
    current_admin: Admin = Depends(require_admin("create:brand")),
):
    return await repo.create(dto.name)


@brand_router.patch("/{brand_id}", response_model=BrandResponse)
async def update(
    brand_id: UUID,
    dto: UpdateBrandRequest,
    repo: BrandRepository = Depends(get_repo),
    current_admin: Admin = Depends(require_admin("update:brand")),
):
    brand = await repo.update(brand_id, dto.name)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Бренд не найден"
        )
    return brand


@brand_router.delete("/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    brand_id: UUID,
    repo: BrandRepository = Depends(get_repo),
    current_admin: Admin = Depends(require_admin("delete:brand")),
):
    deleted = await repo.delete(brand_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Бренд не найден"
        )
