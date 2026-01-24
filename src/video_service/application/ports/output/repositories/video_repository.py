"""Video Repository Interface."""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from video_service.domain.entities.video import Video


class IVideoRepository(ABC):
    """Interface for Video Repository."""

    @abstractmethod
    async def save(self, video: Video) -> Video:
        pass

    @abstractmethod
    async def find_by_id(self, video_id: UUID) -> Optional[Video]:
        pass

    @abstractmethod
    async def find_by_user_id(self, user_id: UUID, skip: int = 0, limit: int = 10) -> List[Video]:
        pass

    @abstractmethod
    async def delete(self, video_id: UUID) -> bool:
        pass

    @abstractmethod
    async def count_by_user_id(self, user_id: UUID) -> int:
        pass
