from datetime import timedelta

import minio
from loguru import logger
from minio import Minio

from src.core.media.application.interfaces.storage import IObjectStorage
from src.core.media.domain.exceptions import MediaNotFoundError


class MinioService(IObjectStorage):
    def __init__(self, bucket_name: str, client: Minio):
        self._bucket_name = bucket_name
        self._client = client

    def generate_upload_url(self, object_name: str, expiration: int = 3600) -> str:
        if not self._client.bucket_exists(self._bucket_name):
            logger.warning(
                "Не удалось найти бакет. Запущено автоматическое создание бакета"
            )
            self._client.make_bucket(self._bucket_name)

        return self._client.get_presigned_url(
            method="PUT",
            bucket_name=self._bucket_name,
            object_name=object_name,
            expires=timedelta(seconds=expiration),
        )

    def generate_download_url(self, object_name: str, expiration: int = 3600) -> str:
        try:
            self._client.stat_object(self._bucket_name, object_name)
        except minio.S3Error as err:
            if err.code in ("NoSuchBucket", "NoSuchKey"):
                raise MediaNotFoundError() from err
            raise

        return self._client.get_presigned_url(
            method="GET",
            bucket_name=self._bucket_name,
            object_name=object_name,
            expires=timedelta(seconds=expiration),
        )
