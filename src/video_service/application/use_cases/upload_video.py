"""Upload Video Use Case."""
from dataclasses import dataclass
from datetime import datetime
from typing import BinaryIO
from uuid import UUID, uuid4

from video_service.domain.entities.video import Video
from video_service.application.ports.output.repositories.video_repository import IVideoRepository
from video_service.application.ports.output.storage_service import IStorageService
from video_service.application.ports.output.event_publisher import IEventPublisher

from video_processor_shared.domain.events import VideoUploadedEvent
from video_processor_shared.domain.exceptions import InvalidVideoFormatError, VideoTooLargeError


@dataclass
class UploadVideoInput:
    user_id: UUID
    filename: str
    file: BinaryIO
    file_size: int
    content_type: str


@dataclass
class VideoOutput:
    id: UUID
    user_id: UUID
    original_filename: str
    file_path: str
    file_size: int
    format: str
    created_at: datetime


class UploadVideoUseCase:
    """Use Case: Upload a video."""

    def __init__(
        self,
        video_repository: IVideoRepository,
        storage_service: IStorageService,
        event_publisher: IEventPublisher,
    ):
        self._video_repository = video_repository
        self._storage_service = storage_service
        self._event_publisher = event_publisher

    async def execute(self, input_data: UploadVideoInput) -> VideoOutput:
        """Execute video upload."""
        # Validate format
        file_format = input_data.filename.rsplit('.', 1)[-1].lower()
        if file_format not in Video.ALLOWED_FORMATS:
            raise InvalidVideoFormatError(f"Format {file_format} not supported")

        # Validate size
        max_size = Video.MAX_SIZE_MB * 1024 * 1024
        if input_data.file_size > max_size:
            raise VideoTooLargeError(f"File exceeds {Video.MAX_SIZE_MB}MB limit")

        # Generate storage path
        video_id = uuid4()
        storage_key = f"videos/{input_data.user_id}/{video_id}.{file_format}"

        # Upload to storage
        file_path = await self._storage_service.upload_file(
            file=input_data.file,
            key=storage_key,
            content_type=input_data.content_type,
        )

        # Create entity
        video = Video(
            id=video_id,
            user_id=input_data.user_id,
            original_filename=input_data.filename,
            file_path=file_path,
            file_size=input_data.file_size,
            format=file_format,
        )

        # Persist
        saved_video = await self._video_repository.save(video)

        # Publish event
        event = VideoUploadedEvent(
            video_id=saved_video.id,
            user_id=saved_video.user_id,
            filename=saved_video.original_filename,
            file_size=saved_video.file_size,
        )
        await self._event_publisher.publish(event)

        return VideoOutput(
            id=saved_video.id,
            user_id=saved_video.user_id,
            original_filename=saved_video.original_filename,
            file_path=saved_video.file_path,
            file_size=saved_video.file_size,
            format=saved_video.format,
            created_at=saved_video.created_at,
        )
