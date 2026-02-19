from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import patch

import httpx
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from video_service.infrastructure.adapters.input.api import dependencies as deps


class _FakeAsyncClient:
    def __init__(self, response=None, exc=None):
        self._response = response
        self._exc = exc

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, *args, **kwargs):
        if self._exc:
            raise self._exc
        return self._response


@pytest.mark.asyncio
async def test_get_current_user_id_success():
    user_id = uuid4()
    response = SimpleNamespace(status_code=200, json=lambda: {"id": str(user_id)})

    with patch("video_service.infrastructure.adapters.input.api.dependencies.httpx.AsyncClient", return_value=_FakeAsyncClient(response=response)):
        result = await deps.get_current_user_id(
            credentials=HTTPAuthorizationCredentials(scheme="Bearer", credentials="token"),
            settings=SimpleNamespace(AUTH_SERVICE_URL="http://auth"),
        )

    assert result == user_id


@pytest.mark.asyncio
async def test_get_current_user_id_invalid_token():
    response = SimpleNamespace(status_code=401, json=lambda: {"detail": "invalid"})

    with patch("video_service.infrastructure.adapters.input.api.dependencies.httpx.AsyncClient", return_value=_FakeAsyncClient(response=response)):
        with pytest.raises(HTTPException) as exc_info:
            await deps.get_current_user_id(
                credentials=HTTPAuthorizationCredentials(scheme="Bearer", credentials="bad"),
                settings=SimpleNamespace(AUTH_SERVICE_URL="http://auth"),
            )

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_id_auth_service_unavailable():
    request = httpx.Request("GET", "http://auth/auth/me")
    error = httpx.RequestError("down", request=request)

    with patch("video_service.infrastructure.adapters.input.api.dependencies.httpx.AsyncClient", return_value=_FakeAsyncClient(exc=error)):
        with pytest.raises(HTTPException) as exc_info:
            await deps.get_current_user_id(
                credentials=HTTPAuthorizationCredentials(scheme="Bearer", credentials="bad"),
                settings=SimpleNamespace(AUTH_SERVICE_URL="http://auth"),
            )

    assert exc_info.value.status_code == 503


@pytest.mark.asyncio
async def test_factory_dependencies_create_expected_adapters():
    db = object()
    repo = await deps.get_video_repository(db=db)
    assert repo.__class__.__name__ == "SQLAlchemyVideoRepository"

    settings = SimpleNamespace(S3_BUCKET="bucket", AWS_ENDPOINT_URL="", AWS_DEFAULT_REGION="us-east-1", SNS_TOPIC_ARN="arn")
    storage = await deps.get_storage_service(settings=settings)
    publisher = await deps.get_event_publisher(settings=settings)

    assert storage.__class__.__name__ == "S3StorageService"
    assert publisher.__class__.__name__ == "SNSEventPublisher"
