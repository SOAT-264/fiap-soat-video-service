from uuid import uuid4

from video_service.infrastructure.adapters.output.persistence.database import Base
from video_service.infrastructure.adapters.output.persistence.models import VideoModel


def test_database_base_and_video_model_mapping():
    assert Base.metadata is not None
    assert VideoModel.__tablename__ == "videos"

    video = VideoModel(
        id=uuid4(),
        user_id=uuid4(),
        original_filename="movie.mp4",
        file_path="s3://bucket/movie.mp4",
        file_size=1024,
        format="mp4",
    )

    assert str(video.file_path).startswith("s3://")
    assert video.original_filename.endswith(".mp4")
