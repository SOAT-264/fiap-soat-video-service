from datetime import datetime
from uuid import uuid4
from unittest.mock import AsyncMock

import pytest

from video_service.application.use_cases.get_video import GetVideoUseCase
from video_service.domain.entities.video import Video
from video_processor_shared.domain.exceptions import VideoNotFoundError


@pytest.mark.asyncio
async def test_get_video_success():
    user_id = uuid4()
    video_id = uuid4()
    repo = AsyncMock()

    expected_video = Video(
        id=video_id,
        user_id=user_id,
        original_filename="movie.mp4",
        file_path="s3://bucket/movie.mp4",
        file_size=123,
        format="mp4",
        created_at=datetime.utcnow(),
    )
    repo.find_by_id.return_value = expected_video

    use_case = GetVideoUseCase(video_repository=repo)
    result = await use_case.execute(video_id=video_id, user_id=user_id)

    assert result.id == video_id
    assert result.user_id == user_id
    repo.find_by_id.assert_awaited_once_with(video_id)


@pytest.mark.asyncio
async def test_get_video_not_found_when_missing():
    repo = AsyncMock()
    repo.find_by_id.return_value = None

    use_case = GetVideoUseCase(video_repository=repo)

    with pytest.raises(VideoNotFoundError):
        await use_case.execute(video_id=uuid4(), user_id=uuid4())


@pytest.mark.asyncio
async def test_get_video_not_found_when_other_user():
    owner_id = uuid4()
    requested_by = uuid4()
    video_id = uuid4()

    repo = AsyncMock()
    repo.find_by_id.return_value = Video(
        id=video_id,
        user_id=owner_id,
        original_filename="movie.mp4",
        file_path="s3://bucket/movie.mp4",
        file_size=123,
        format="mp4",
    )

    use_case = GetVideoUseCase(video_repository=repo)

    with pytest.raises(VideoNotFoundError):
        await use_case.execute(video_id=video_id, user_id=requested_by)
