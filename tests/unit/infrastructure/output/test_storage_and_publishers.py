from io import BytesIO
from types import SimpleNamespace

import pytest

from video_service.infrastructure.adapters.output.messaging.sns_publisher import SNSEventPublisher
from video_service.infrastructure.adapters.output.messaging.sqs_publisher import SQSJobPublisher
from video_service.infrastructure.adapters.output.storage.s3_storage import S3StorageService


class _FakeClient:
    def __init__(self, service_name, record):
        self._service_name = service_name
        self._record = record

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def upload_fileobj(self, file_obj, bucket, key, ExtraArgs):
        self._record.append((self._service_name, "upload_fileobj", bucket, key, ExtraArgs))

    async def generate_presigned_url(self, operation, Params, ExpiresIn):
        self._record.append((self._service_name, "generate_presigned_url", operation, Params, ExpiresIn))
        return "https://presigned"

    async def delete_object(self, Bucket, Key):
        self._record.append((self._service_name, "delete_object", Bucket, Key))

    async def publish(self, **kwargs):
        self._record.append((self._service_name, "publish", kwargs))

    async def send_message(self, **kwargs):
        self._record.append((self._service_name, "send_message", kwargs))
        return {"MessageId": "msg-1"}


class _FakeSession:
    def __init__(self, record):
        self._record = record

    def client(self, service_name, **kwargs):
        self._record.append((service_name, "client", kwargs))
        return _FakeClient(service_name, self._record)


@pytest.mark.asyncio
async def test_s3_storage_service_methods(monkeypatch):
    record = []
    monkeypatch.setattr(
        "video_service.infrastructure.adapters.output.storage.s3_storage.aioboto3.Session",
        lambda: _FakeSession(record),
    )

    service = S3StorageService(bucket="bucket", endpoint_url="http://local", region="us-east-1")

    path = await service.upload_file(BytesIO(b"123"), "videos/file.mp4", "video/mp4")
    url = await service.get_presigned_url("videos/file.mp4", expires_in=10)
    deleted = await service.delete_file("videos/file.mp4")

    assert path == "s3://bucket/videos/file.mp4"
    assert url == "https://presigned"
    assert deleted is True
    assert any(item[1] == "upload_fileobj" for item in record)
    assert any(item[1] == "generate_presigned_url" for item in record)
    assert any(item[1] == "delete_object" for item in record)


@pytest.mark.asyncio
async def test_sns_publisher_with_and_without_topic(monkeypatch):
    record = []
    monkeypatch.setattr(
        "video_service.infrastructure.adapters.output.messaging.sns_publisher.aioboto3.Session",
        lambda: _FakeSession(record),
    )

    class _Event:
        event_type = "VideoUploaded"

        def to_dict(self):
            return {"id": "1"}

    publisher = SNSEventPublisher(topic_arn="arn", endpoint_url="http://local")
    await publisher.publish(_Event())
    assert any(item[1] == "publish" for item in record)

    record.clear()
    publisher_without_topic = SNSEventPublisher(topic_arn="")
    await publisher_without_topic.publish(_Event())
    assert record == []


@pytest.mark.asyncio
async def test_sqs_job_publisher_send_job(monkeypatch):
    record = []
    monkeypatch.setattr(
        "video_service.infrastructure.adapters.output.messaging.sqs_publisher.aioboto3.Session",
        lambda: _FakeSession(record),
    )

    publisher = SQSJobPublisher(queue_url="queue-url", endpoint_url="http://local")
    message_id = await publisher.send_job(
        job_id="job-1",
        video_id="video-1",
        user_id="user-1",
        s3_key="videos/file.mp4",
        user_email="user@email.com",
    )

    assert message_id == "msg-1"
    assert any(item[1] == "send_message" for item in record)
