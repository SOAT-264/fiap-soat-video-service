from datetime import datetime, timedelta
from uuid import uuid4
from unittest.mock import AsyncMock

import pytest

from video_service.application.use_cases.list_videos import ListVideosUseCase
from video_service.domain.entities.video import Video


@pytest.mark.asyncio
async def test_list_videos_with_pagination():
    user_id = uuid4()
    now = datetime.utcnow()

    video1 = Video(
        id=uuid4(),
        user_id=user_id,
        original_filename="v1.mp4",
        file_path="s3://bucket/v1.mp4",
        file_size=100,
        format="mp4",
        created_at=now,
    )
    video2 = Video(
        id=uuid4(),
        user_id=user_id,
        original_filename="v2.mp4",
        file_path="s3://bucket/v2.mp4",
        file_size=200,
        format="mp4",
        created_at=now - timedelta(minutes=1),
    )

    repo = AsyncMock()
    repo.find_by_user_id.return_value = [video1, video2]
    repo.count_by_user_id.return_value = 11

    use_case = ListVideosUseCase(video_repository=repo)
    result = await use_case.execute(user_id=user_id, page=2, page_size=5)

    assert result.total == 11
    assert result.page == 2
    assert result.page_size == 5
    assert len(result.videos) == 2
    assert result.videos[0].original_filename == "v1.mp4"

    repo.find_by_user_id.assert_awaited_once_with(user_id, 5, 5)
    repo.count_by_user_id.assert_awaited_once_with(user_id)
