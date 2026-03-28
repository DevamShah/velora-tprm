"""
MinIO (S3-compatible) storage client for evidence documents.

Handles upload with presigned URLs and download for parsing.
"""

from __future__ import annotations

import os
from io import BytesIO
from typing import Optional

from minio import Minio
from minio.error import S3Error

from velora_common.logging import get_logger

logger = get_logger(__name__)

_DEFAULT_BUCKET = "velora-evidence"
_PRESIGNED_EXPIRY = 3600  # 1 hour


class StorageClient:
    """MinIO storage for evidence documents."""

    def __init__(
        self,
        endpoint: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        bucket: str = _DEFAULT_BUCKET,
        secure: bool = False,
    ) -> None:
        self._endpoint = endpoint or os.environ.get(
            "MINIO_ENDPOINT", "minio:9000"
        )
        self._access_key = access_key or os.environ.get(
            "MINIO_ACCESS_KEY", ""
        )
        self._secret_key = secret_key or os.environ.get(
            "MINIO_SECRET_KEY", ""
        )
        if not self._access_key or not self._secret_key:
            raise ValueError(
                "MINIO_ACCESS_KEY and MINIO_SECRET_KEY "
                "must be set in environment"
            )
        self._bucket = bucket
        self._secure = secure

        self._client = Minio(
            self._endpoint,
            access_key=self._access_key,
            secret_key=self._secret_key,
            secure=self._secure,
        )
        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        """Create bucket if it doesn't exist."""
        try:
            if not self._client.bucket_exists(
                self._bucket
            ):
                self._client.make_bucket(self._bucket)
                logger.info(
                    "bucket_created",
                    bucket=self._bucket,
                )
        except S3Error as exc:
            logger.error(
                "bucket_check_failed",
                error=str(exc),
            )

    def get_presigned_upload_url(
        self, s3_key: str
    ) -> str:
        """Generate presigned PUT URL for upload."""
        from datetime import timedelta

        url = self._client.presigned_put_object(
            self._bucket,
            s3_key,
            expires=timedelta(seconds=_PRESIGNED_EXPIRY),
        )
        return url

    def get_presigned_download_url(
        self, s3_key: str
    ) -> str:
        """Generate presigned GET URL for download."""
        from datetime import timedelta

        url = self._client.presigned_get_object(
            self._bucket,
            s3_key,
            expires=timedelta(seconds=_PRESIGNED_EXPIRY),
        )
        return url

    def download_bytes(self, s3_key: str) -> bytes:
        """Download file content as bytes for parsing."""
        try:
            response = self._client.get_object(
                self._bucket, s3_key
            )
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as exc:
            logger.error(
                "download_failed",
                s3_key=s3_key,
                error=str(exc),
            )
            raise

    def upload_bytes(
        self,
        s3_key: str,
        data: bytes,
        content_type: str = "application/pdf",
    ) -> None:
        """Upload file bytes directly."""
        try:
            self._client.put_object(
                self._bucket,
                s3_key,
                BytesIO(data),
                length=len(data),
                content_type=content_type,
            )
            logger.info(
                "file_uploaded",
                s3_key=s3_key,
                size=len(data),
            )
        except S3Error as exc:
            logger.error(
                "upload_failed",
                s3_key=s3_key,
                error=str(exc),
            )
            raise
