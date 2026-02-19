from datetime import datetime
from io import BytesIO
from uuid import uuid4
from unittest.mock import AsyncMock, patch

import pytest

from video_service.application.use_cases.upload_video import UploadVideoUseCase, UploadVideoInput
from video_service.domain.entities.video import Video
from video_processor_shared.domain.exceptions import InvalidVideoFormatError, VideoTooLargeError


@pytest.mark.asyncio
async def test_upload_video_success_persists_and_publishes_event():
    user_id = uuid4()
    generated_id = uuid4()

    repo = AsyncMock()
    storage = AsyncMock()
    publisher = AsyncMock()

    created_at = datetime.utcnow()
    saved_video = Video(
        id=generated_id,
        user_id=user_id,
        original_filename="movie.mp4",
        file_path="s3://video-uploads/videos/file.mp4",
        file_size=1024,
        format="mp4",
        created_at=created_at,
    )

    storage.upload_file.return_value = saved_video.file_path
    repo.save.return_value = saved_video

    use_case = UploadVideoUseCase(repo, storage, publisher)

    with patch("video_service.application.use_cases.upload_video.uuid4", return_value=generated_id):
        result = await use_case.execute(
            UploadVideoInput(
                user_id=user_id,
                filename="movie.mp4",
                file=BytesIO(b"abc"),
                file_size=1024,
                content_type="video/mp4",
            )
        )

    assert result.id == generated_id
    assert result.file_path == saved_video.file_path

    storage.upload_file.assert_awaited_once()
    repo.save.assert_awaited_once()
    publisher.publish.assert_awaited_once()


@pytest.mark.asyncio
async def test_upload_video_invalid_format_raises_error():
    use_case = UploadVideoUseCase(AsyncMock(), AsyncMock(), AsyncMock())

    with pytest.raises(InvalidVideoFormatError):
        await use_case.execute(
            UploadVideoInput(
                user_id=uuid4(),
                filename="movie.txt",
                file=BytesIO(b"abc"),
                file_size=123,
                content_type="text/plain",
            )
        )


@pytest.mark.asyncio
async def test_upload_video_too_large_raises_error():
    use_case = UploadVideoUseCase(AsyncMock(), AsyncMock(), AsyncMock())

    with pytest.raises(VideoTooLargeError):
        await use_case.execute(
            UploadVideoInput(
                user_id=uuid4(),
                filename="movie.mp4",
                file=BytesIO(b"abc"),
                file_size=(Video.MAX_SIZE_MB * 1024 * 1024) + 1,
                content_type="video/mp4",
            )
        )
