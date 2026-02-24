from typing import Optional
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from video_service.domain.entities.video import Video
from video_service.infrastructure.adapters.input.api.dependencies import (
    get_current_user_id,
    get_event_publisher,
    get_storage_service,
    get_video_repository,
)
from video_service.infrastructure.adapters.input.api.main import create_app


class InMemoryVideoRepository:
    def __init__(self):
        self.items: dict[UUID, Video] = {}

    async def save(self, video: Video) -> Video:
        self.items[video.id] = video
        return video

    async def find_by_id(self, video_id: UUID) -> Optional[Video]:
        return self.items.get(video_id)

    async def find_by_user_id(self, user_id: UUID, skip: int = 0, limit: int = 10):
        filtered = [v for v in self.items.values() if v.user_id == user_id]
        return filtered[skip : skip + limit]

    async def delete(self, video_id: UUID) -> bool:
        return self.items.pop(video_id, None) is not None

    async def count_by_user_id(self, user_id: UUID) -> int:
        return len([v for v in self.items.values() if v.user_id == user_id])


class InMemoryStorageService:
    async def upload_file(self, file, key: str, content_type: str) -> str:
        return f"s3://bucket/{key}"

    async def get_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        return "https://presigned"

    async def delete_file(self, key: str) -> bool:
        return True


class NullEventPublisher:
    async def publish(self, event) -> None:
        return None


def _build_client(user_id: UUID):
    app = create_app()
    repo = InMemoryVideoRepository()

    app.dependency_overrides[get_current_user_id] = lambda: user_id
    app.dependency_overrides[get_video_repository] = lambda: repo
    app.dependency_overrides[get_storage_service] = lambda: InMemoryStorageService()
    app.dependency_overrides[get_event_publisher] = lambda: NullEventPublisher()

    return TestClient(app), repo


def test_health_endpoint(monkeypatch):
    async def _fake_init_db():
        return None

    monkeypatch.setattr("video_service.infrastructure.adapters.input.api.main.init_db", _fake_init_db)

    client, _ = _build_client(user_id=uuid4())
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_upload_and_get_and_list_flow(monkeypatch):
    async def _fake_init_db():
        return None

    monkeypatch.setattr("video_service.infrastructure.adapters.input.api.main.init_db", _fake_init_db)

    user_id = uuid4()
    client, _ = _build_client(user_id=user_id)

    upload_response = client.post(
        "/videos/upload",
        files=[("files", ("movie.mp4", b"binary-content", "video/mp4"))],
    )
    assert upload_response.status_code == 201
    payload = upload_response.json()
    assert len(payload) == 1
    assert payload[0]["original_filename"] == "movie.mp4"

    video_id = payload[0]["id"]

    get_response = client.get(f"/videos/{video_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == video_id

    list_response = client.get("/videos?page=1&page_size=10")
    assert list_response.status_code == 200
    assert list_response.json()["total"] >= 1


def test_upload_invalid_format_returns_400(monkeypatch):
    async def _fake_init_db():
        return None

    monkeypatch.setattr("video_service.infrastructure.adapters.input.api.main.init_db", _fake_init_db)

    client, _ = _build_client(user_id=uuid4())

    response = client.post(
        "/videos/upload",
        files=[("files", ("movie.txt", b"content", "text/plain"))],
    )

    assert response.status_code == 400


def test_get_video_not_found_returns_404(monkeypatch):
    async def _fake_init_db():
        return None

    monkeypatch.setattr("video_service.infrastructure.adapters.input.api.main.init_db", _fake_init_db)

    client, _ = _build_client(user_id=uuid4())

    response = client.get(f"/videos/{uuid4()}")
    assert response.status_code == 404


def test_list_videos_query_validation(monkeypatch):
    async def _fake_init_db():
        return None

    monkeypatch.setattr("video_service.infrastructure.adapters.input.api.main.init_db", _fake_init_db)

    client, _ = _build_client(user_id=uuid4())

    response = client.get("/videos?page=0&page_size=101")
    assert response.status_code == 422
