"""S3 Storage Service."""
from typing import BinaryIO, Optional
import aioboto3

from video_service.application.ports.output.storage_service import IStorageService


class S3StorageService(IStorageService):
    def __init__(self, bucket: str, endpoint_url: Optional[str] = None, region: str = "us-east-1"):
        self._bucket = bucket
        self._endpoint_url = endpoint_url
        self._region = region
        self._session = aioboto3.Session()

    async def upload_file(self, file: BinaryIO, key: str, content_type: str) -> str:
        async with self._session.client(
            's3',
            endpoint_url=self._endpoint_url,
            region_name=self._region,
        ) as s3:
            await s3.upload_fileobj(
                file,
                self._bucket,
                key,
                ExtraArgs={'ContentType': content_type},
            )
        return f"s3://{self._bucket}/{key}"

    async def get_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        async with self._session.client(
            's3',
            endpoint_url=self._endpoint_url,
            region_name=self._region,
        ) as s3:
            return await s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': self._bucket, 'Key': key},
                ExpiresIn=expires_in,
            )

    async def delete_file(self, key: str) -> bool:
        async with self._session.client(
            's3',
            endpoint_url=self._endpoint_url,
            region_name=self._region,
        ) as s3:
            await s3.delete_object(Bucket=self._bucket, Key=key)
            return True
