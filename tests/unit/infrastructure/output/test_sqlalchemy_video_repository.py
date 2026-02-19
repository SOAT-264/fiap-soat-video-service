from datetime import datetime
from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

import pytest

from video_service.domain.entities.video import Video
from video_service.infrastructure.adapters.output.persistence.repositories.video_repository import (
    SQLAlchemyVideoRepository,
)


class _ScalarRows:
    def __init__(self, rows):
        self._rows = rows

    def all(self):
        return self._rows


class _Result:
    def __init__(self, one=None, rows=None, scalar_value=None):
        self._one = one
        self._rows = rows or []
        self._scalar_value = scalar_value

    def scalar_one_or_none(self):
        return self._one

    def scalars(self):
        return _ScalarRows(self._rows)

    def scalar(self):
        return self._scalar_value


@pytest.mark.asyncio
async def test_save_adds_and_flushes_session():
    session = SimpleNamespace(add=MagicMock(), flush=AsyncMock(), execute=AsyncMock(), delete=AsyncMock())
    repo = SQLAlchemyVideoRepository(session=session)

    video = Video(
        id=uuid4(),
        user_id=uuid4(),
        original_filename="movie.mp4",
        file_path="s3://bucket/movie.mp4",
        file_size=100,
        format="mp4",
    )

    result = await repo.save(video)

    assert result == video
    session.add.assert_called_once()
    session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_find_by_id_returns_entity_or_none():
    session = SimpleNamespace(add=MagicMock(), flush=AsyncMock(), execute=AsyncMock(), delete=AsyncMock())
    repo = SQLAlchemyVideoRepository(session=session)

    model = SimpleNamespace(
        id=uuid4(),
        user_id=uuid4(),
        original_filename="movie.mp4",
        file_path="s3://bucket/movie.mp4",
        file_size=100,
        format="mp4",
        duration=10.0,
        created_at=datetime.utcnow(),
    )

    session.execute.return_value = _Result(one=model)
    found = await repo.find_by_id(model.id)
    assert found is not None
    assert found.id == model.id

    session.execute.return_value = _Result(one=None)
    not_found = await repo.find_by_id(uuid4())
    assert not_found is None


@pytest.mark.asyncio
async def test_find_by_user_id_delete_and_count():
    session = SimpleNamespace(add=MagicMock(), flush=AsyncMock(), execute=AsyncMock(), delete=AsyncMock())
    repo = SQLAlchemyVideoRepository(session=session)

    m1 = SimpleNamespace(
        id=uuid4(),
        user_id=uuid4(),
        original_filename="1.mp4",
        file_path="s3://bucket/1.mp4",
        file_size=100,
        format="mp4",
        duration=None,
        created_at=datetime.utcnow(),
    )
    m2 = SimpleNamespace(
        id=uuid4(),
        user_id=m1.user_id,
        original_filename="2.mp4",
        file_path="s3://bucket/2.mp4",
        file_size=200,
        format="mp4",
        duration=None,
        created_at=datetime.utcnow(),
    )

    session.execute.return_value = _Result(rows=[m1, m2])
    videos = await repo.find_by_user_id(m1.user_id, 0, 10)
    assert len(videos) == 2

    session.execute.return_value = _Result(one=m1)
    deleted = await repo.delete(m1.id)
    assert deleted is True
    session.delete.assert_awaited_once()
    session.flush.assert_awaited_once()

    session.delete.reset_mock()
    session.flush.reset_mock()

    session.execute.return_value = _Result(one=None)
    deleted = await repo.delete(uuid4())
    assert deleted is False
    session.delete.assert_not_awaited()

    session.execute.return_value = _Result(scalar_value=7)
    count = await repo.count_by_user_id(m1.user_id)
    assert count == 7

    session.execute.return_value = _Result(scalar_value=None)
    count = await repo.count_by_user_id(m1.user_id)
    assert count == 0
