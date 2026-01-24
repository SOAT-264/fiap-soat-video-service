"""Storage Service Interface."""
from abc import ABC, abstractmethod
from typing import BinaryIO


class IStorageService(ABC):
    """Interface for Storage Service (S3)."""

    @abstractmethod
    async def upload_file(self, file: BinaryIO, key: str, content_type: str) -> str:
        """Upload file and return the storage path."""
        pass

    @abstractmethod
    async def get_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """Get presigned URL for download."""
        pass

    @abstractmethod
    async def delete_file(self, key: str) -> bool:
        """Delete file from storage."""
        pass
