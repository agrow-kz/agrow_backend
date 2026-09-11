from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends

from src.configuration.dependencies.container import ApplicationContainer
from src.core.admin.domain.entities import Admin
from src.core.references.infrastructure.repositories.country import CountryRepository
from src.core.references.presentation.dto.country import (
    CountryResponse,
    CreateCountryRequest,
    UpdateCountryRequest,
)
from src.core.shared.presentation.security import require_admin

country_router = APIRouter(prefix="/country")


@inject
async def get_repo(
    repo: Annotated[
        CountryRepository,
        Depends(Provide[ApplicationContainer.reference.country_repository]),
    ],
) -> CountryRepository:
    return repo


@country_router.get("/", response_model=list[CountryResponse])
async def get_all(repo: CountryRepository = Depends(get_repo)):
    return await repo.get_all()


@country_router.get("/{country_id}", response_model=CountryResponse)
async def get_by_id(country_id: UUID, repo: CountryRepository = Depends(get_repo)):
    country = await repo.get_by_id(country_id)
    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Страна не найдена"
        )
    return country


@country_router.post(
    "/", response_model=CountryResponse, status_code=status.HTTP_201_CREATED
)
async def create(
    dto: CreateCountryRequest,
    repo: CountryRepository = Depends(get_repo),
    current_admin: Admin = Depends(require_admin("create:country")),
):
    return await repo.create(dto.name)


@country_router.patch("/{country_id}", response_model=CountryResponse)
async def update(
    country_id: UUID,
    dto: UpdateCountryRequest,
    repo: CountryRepository = Depends(get_repo),
    current_admin: Admin = Depends(require_admin("update:country")),
):
    country = await repo.update(country_id, dto.name)
    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Страна не найдена"
        )
    return country


@country_router.delete("/{country_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    country_id: UUID,
    repo: CountryRepository = Depends(get_repo),
    current_admin: Admin = Depends(require_admin("delete:country")),
):
    deleted = await repo.delete(country_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Страна не найдена"
        )
