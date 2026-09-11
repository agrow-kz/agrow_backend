from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends

from src.configuration.dependencies.container import ApplicationContainer
from src.core.admin.domain.entities import Admin
from src.core.references.infrastructure.repositories.region import RegionRepository
from src.core.references.presentation.dto.region import (
    CreateRegionRequest,
    RegionResponse,
    UpdateRegionRequest,
)
from src.core.shared.presentation.security import require_admin

region_router = APIRouter(prefix="/region")


@inject
async def get_repo(
    repo: Annotated[
        RegionRepository,
        Depends(Provide[ApplicationContainer.reference.region_repository]),
    ],
) -> RegionRepository:
    return repo


@region_router.get("/", response_model=list[RegionResponse])
async def get_all(repo: RegionRepository = Depends(get_repo)):
    return await repo.get_all()


@region_router.get("/{region_id}", response_model=RegionResponse)
async def get_by_id(region_id: UUID, repo: RegionRepository = Depends(get_repo)):
    region = await repo.get_by_id(region_id)
    if not region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Регион не найден"
        )
    return region


@region_router.post(
    "/", response_model=RegionResponse, status_code=status.HTTP_201_CREATED
)
async def create(
    dto: CreateRegionRequest,
    repo: RegionRepository = Depends(get_repo),
    current_admin: Admin = Depends(require_admin("create:region")),
):
    return await repo.create(dto.name)


@region_router.patch("/{region_id}", response_model=RegionResponse)
async def update(
    region_id: UUID,
    dto: UpdateRegionRequest,
    repo: RegionRepository = Depends(get_repo),
    current_admin: Admin = Depends(require_admin("update:region")),
):
    region = await repo.update(region_id, dto.name)
    if not region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Регион не найден"
        )
    return region


@region_router.delete("/{region_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    region_id: UUID,
    repo: RegionRepository = Depends(get_repo),
    current_admin: Admin = Depends(require_admin("delete:region")),
):
    deleted = await repo.delete(region_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Регион не найден"
        )
