"""List Videos Use Case."""
from dataclasses import dataclass
from typing import List
from uuid import UUID

from video_service.application.ports.output.repositories.video_repository import IVideoRepository
from video_service.application.use_cases.upload_video import VideoOutput


@dataclass
class PaginatedVideosOutput:
    videos: List[VideoOutput]
    total: int
    page: int
    page_size: int


class ListVideosUseCase:
    """Use Case: List videos for a user."""

    def __init__(self, video_repository: IVideoRepository):
        self._video_repository = video_repository

    async def execute(
        self,
        user_id: UUID,
        page: int = 1,
        page_size: int = 10,
    ) -> PaginatedVideosOutput:
        """List videos with pagination."""
        skip = (page - 1) * page_size
        videos = await self._video_repository.find_by_user_id(user_id, skip, page_size)
        total = await self._video_repository.count_by_user_id(user_id)

        return PaginatedVideosOutput(
            videos=[
                VideoOutput(
                    id=v.id,
                    user_id=v.user_id,
                    original_filename=v.original_filename,
                    file_path=v.file_path,
                    file_size=v.file_size,
                    format=v.format,
                    created_at=v.created_at,
                )
                for v in videos
            ],
            total=total,
            page=page,
            page_size=page_size,
        )
