from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends

from src.configuration.dependencies.container import ApplicationContainer
from src.core.admin.domain.entities import Admin
from src.core.references.infrastructure.repositories.color import ColorRepository
from src.core.references.presentation.dto.color import (
    ColorResponse,
    CreateColorRequest,
    UpdateColorRequest,
)
from src.core.shared.presentation.security import require_admin

color_router = APIRouter(prefix="/color")


@inject
async def get_repo(
    repo: Annotated[
        ColorRepository,
        Depends(Provide[ApplicationContainer.reference.color_repository]),
    ],
) -> ColorRepository:
    return repo


@color_router.get("/", response_model=list[ColorResponse])
async def get_all(repo: ColorRepository = Depends(get_repo)):
    return await repo.get_all()


@color_router.get("/{color_id}", response_model=ColorResponse)
async def get_by_id(color_id: UUID, repo: ColorRepository = Depends(get_repo)):
    color = await repo.get_by_id(color_id)
    if not color:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Цвет не найден"
        )
    return color


@color_router.post(
    "/", response_model=ColorResponse, status_code=status.HTTP_201_CREATED
)
async def create(
    dto: CreateColorRequest,
    repo: ColorRepository = Depends(get_repo),
    current_admin: Admin = Depends(require_admin("create:color")),
):
    return await repo.create(dto.name, dto.hex)


@color_router.patch("/{color_id}", response_model=ColorResponse)
async def update(
    color_id: UUID,
    dto: UpdateColorRequest,
    repo: ColorRepository = Depends(get_repo),
    current_admin: Admin = Depends(require_admin("update:color")),
):
    color = await repo.update(color_id, dto.name, dto.hex)
    if not color:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Цвет не найден"
        )
    return color


@color_router.delete("/{color_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    color_id: UUID,
    repo: ColorRepository = Depends(get_repo),
    current_admin: Admin = Depends(require_admin("delete:color")),
):
    deleted = await repo.delete(color_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Цвет не найден"
        )
