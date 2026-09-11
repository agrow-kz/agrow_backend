from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends

from src.configuration.dependencies.container import ApplicationContainer
from src.core.admin.domain.entities import Admin
from src.core.references.infrastructure.repositories.city import CityRepository
from src.core.references.presentation.dto.city import (
    CityResponse,
    CreateCityRequest,
    UpdateCityRequest,
)
from src.core.shared.presentation.security import require_admin

city_router = APIRouter(prefix="/city")


@inject
async def get_repo(
    repo: Annotated[
        CityRepository, Depends(Provide[ApplicationContainer.reference.city_repository])
    ],
) -> CityRepository:
    return repo


@city_router.get("/", response_model=list[CityResponse])
async def get_all(repo: CityRepository = Depends(get_repo)):
    return await repo.get_all()


@city_router.get("/{city_id}", response_model=CityResponse)
async def get_by_id(city_id: UUID, repo: CityRepository = Depends(get_repo)):
    city = await repo.get_by_id(city_id)
    if not city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Город не найден"
        )
    return city


@city_router.get("/by-region/{region_id}", response_model=list[CityResponse])
async def get_by_region(region_id: UUID, repo: CityRepository = Depends(get_repo)):
    return await repo.get_by_region(region_id)


@city_router.post("/", response_model=CityResponse, status_code=status.HTTP_201_CREATED)
async def create(
    dto: CreateCityRequest,
    repo: CityRepository = Depends(get_repo),
    current_admin: Admin = Depends(require_admin("create:city")),
):
    return await repo.create(dto.name, dto.region_id)


@city_router.patch("/{city_id}", response_model=CityResponse)
async def update(
    city_id: UUID,
    dto: UpdateCityRequest,
    repo: CityRepository = Depends(get_repo),
    current_admin: Admin = Depends(require_admin("update:city")),
):
    city = await repo.update(city_id, dto.name, dto.region_id)
    if not city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Город не найден"
        )
    return city


@city_router.delete("/{city_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    city_id: UUID,
    repo: CityRepository = Depends(get_repo),
    current_admin: Admin = Depends(require_admin("delete:city")),
):
    deleted = await repo.delete(city_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Город не найден"
        )
