from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.configuration.dependencies.container import ApplicationContainer
from src.core.admin.domain.entities import Admin
from src.core.catalog.infrastructure.repositories.attributes import (
    UnitOfMeasureRepository,
)
from src.core.catalog.presentation.dto.attributes import (
    CreateUnitOfMeasureRequest,
    UnitOfMeasureResponse,
)
from src.core.shared.presentation.security import require_admin

unit_of_measure_router = APIRouter(prefix="/unit-of-measure")


@unit_of_measure_router.post("/", response_model=UnitOfMeasureResponse)
@inject
async def create_unit_of_measure(
    dto: CreateUnitOfMeasureRequest,
    repo: Annotated[
        UnitOfMeasureRepository,
        Depends(Provide[ApplicationContainer.catalog.unit_of_measure_repository]),
    ],
    current_admin: Admin = Depends(require_admin("create:unit")),
):
    unit = await repo.create(key=dto.key, label=dto.label)
    return unit


@unit_of_measure_router.get("/", response_model=list[UnitOfMeasureResponse])
@inject
async def get_all_units(
    repo: Annotated[
        UnitOfMeasureRepository,
        Depends(Provide[ApplicationContainer.catalog.unit_of_measure_repository]),
    ],
):
    return await repo.get_all()
