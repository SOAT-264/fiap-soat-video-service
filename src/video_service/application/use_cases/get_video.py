"""Get Video Use Case."""
from uuid import UUID

from video_service.application.ports.output.repositories.video_repository import IVideoRepository
from video_service.application.use_cases.upload_video import VideoOutput

from video_processor_shared.domain.exceptions import VideoNotFoundError


class GetVideoUseCase:
    """Use Case: Get a video by ID."""

    def __init__(self, video_repository: IVideoRepository):
        self._video_repository = video_repository

    async def execute(self, video_id: UUID, user_id: UUID) -> VideoOutput:
        """Get video by ID."""
        video = await self._video_repository.find_by_id(video_id)
        if not video:
            raise VideoNotFoundError(f"Video {video_id} not found")

        if video.user_id != user_id:
            raise VideoNotFoundError(f"Video {video_id} not found")

        return VideoOutput(
            id=video.id,
            user_id=video.user_id,
            original_filename=video.original_filename,
            file_path=video.file_path,
            file_size=video.file_size,
            format=video.format,
            created_at=video.created_at,
        )
