from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter
from fastapi.params import Depends, Security
from fastapi.responses import RedirectResponse

from src.configuration.dependencies.container import ApplicationContainer
from src.core.media.application.services.media_service import MediaService
from src.core.media.presentation.dto import (
    ConfirmUploadRequest,
    ConfirmUploadResponse,
    GenerateUploadUrlRequest,
    UploadUrlResponse,
)
from src.core.shared.presentation.dto import CurrentUser
from src.core.shared.presentation.security import get_current_user

media_router = APIRouter(prefix="/api/v1/media", tags=["Media"])


@media_router.post("/upload-url", response_model=list[UploadUrlResponse])
@inject
async def generate_upload_url(
    dto: GenerateUploadUrlRequest,
    service: Annotated[
        MediaService, Depends(Provide[ApplicationContainer.media.media_service])
    ],
    current_user: CurrentUser = Security(get_current_user),
):
    return await service.generate_upload_url(dto)


@media_router.post("/confirm-upload", response_model=list[ConfirmUploadResponse])
@inject
async def confirm_upload(
    dto: ConfirmUploadRequest,
    service: Annotated[
        MediaService, Depends(Provide[ApplicationContainer.media.media_service])
    ],
    current_user: CurrentUser = Security(get_current_user),
):
    media_response = await service.confirm_upload(current_user.id, dto)
    return media_response


@media_router.get("/{media_id}")
@inject
async def get_media(
    media_id: UUID,
    service: Annotated[
        MediaService, Depends(Provide[ApplicationContainer.media.media_service])
    ],
):
    url = await service.get_media_url(media_id)
    return RedirectResponse(url)
