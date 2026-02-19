from datetime import datetime
from uuid import uuid4

from video_service.domain.entities.video import Video


def test_video_properties_and_validation():
    video = Video(
        id=uuid4(),
        user_id=uuid4(),
        original_filename="movie.MP4",
        file_path="s3://bucket/movie.mp4",
        file_size=20 * 1024 * 1024,
        format="MP4",
    )

    assert round(video.file_size_mb, 2) == 20.0
    assert video.is_valid_format is True
    assert video.is_valid_size is True
    assert video.format == "mp4"


def test_video_invalid_format_and_size_and_duration():
    video = Video(
        id=uuid4(),
        user_id=uuid4(),
        original_filename="movie.wmv",
        file_path="s3://bucket/movie.wmv",
        file_size=600 * 1024 * 1024,
        format="wmv",
    )

    video.set_duration(90.5)

    assert video.is_valid_format is False
    assert video.is_valid_size is False
    assert video.duration == 90.5


def test_video_equality_hash_and_created_at_default():
    video_id = uuid4()
    user_id = uuid4()

    video1 = Video(
        id=video_id,
        user_id=user_id,
        original_filename="movie.mp4",
        file_path="s3://bucket/movie.mp4",
        file_size=1024,
        format="mp4",
    )
    video2 = Video(
        id=video_id,
        user_id=user_id,
        original_filename="movie2.mp4",
        file_path="s3://bucket/movie2.mp4",
        file_size=2048,
        format="mp4",
    )

    assert isinstance(video1.created_at, datetime)
    assert video1 == video2
    assert hash(video1) == hash(video2)
    assert (video1 == object()) is False
