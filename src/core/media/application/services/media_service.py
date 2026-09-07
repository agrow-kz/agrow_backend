import uuid
from uuid import UUID

from loguru import logger

from src.core.media.application.interfaces.storage import IObjectStorage
from src.core.media.domain.entities import Media
from src.core.media.domain.value_objects import MediaSize
from src.core.media.infrastructure.uow import MediaUnitOfWork
from src.core.media.presentation.dto import (
    ConfirmUploadRequest,
    ConfirmUploadResponse,
    GenerateUploadUrlRequest,
    UploadUrlResponse,
)


class MediaService:
    def __init__(self, uow: MediaUnitOfWork, storage: IObjectStorage):
        self.uow = uow
        self.storage = storage

    async def generate_upload_url(
        self, dto: GenerateUploadUrlRequest
    ) -> list[UploadUrlResponse]:
        response = []

        for file in dto.files:
            unique_key = uuid.uuid4()
            object_key = f"uploads/{unique_key}/{file.client_filename}"

            upload_url = self.storage.generate_upload_url(object_name=object_key)
            response.append(
                UploadUrlResponse(
                    client_filename=file.client_filename,
                    upload_url=upload_url,
                    file_path=object_key,
                )
            )

        return response

    async def confirm_upload(
        self, account_id: UUID, dto: ConfirmUploadRequest
    ) -> list[ConfirmUploadResponse]:
        async with self.uow as uow:
            media_list = [
                Media.create(
                    owner_id=account_id,
                    media_url=item.file_path,
                    media_type=item.media_type,
                    media_size=MediaSize(item.media_size),
                )
                for item in dto.files
            ]

            await uow.media.save(media_list)
            await uow.commit()

        logger.info("Confirming upload media | account_id={}", account_id)
        return [
            ConfirmUploadResponse(
                media_id=media.id,
                media_type=media.media_type,
                media_size=media.media_size.value,
            )
            for media in media_list
        ]

    async def get_media_url(self, media_id: UUID) -> str | None:
        async with self.uow as uow:
            media = await uow.media.get_by_id(media_id)
            if not media:
                return None
        return self.storage.generate_download_url(media.media_url)
