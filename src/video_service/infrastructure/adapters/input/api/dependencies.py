"""API Dependencies."""
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx

from video_service.infrastructure.config import get_settings, Settings
from video_service.application.ports.output.repositories import IVideoRepository
from video_service.application.ports.output.storage_service import IStorageService
from video_service.application.ports.output.event_publisher import IEventPublisher
from video_service.infrastructure.adapters.output.persistence.repositories import SQLAlchemyVideoRepository
from video_service.infrastructure.adapters.output.persistence.database import get_db
from video_service.infrastructure.adapters.output.storage.s3_storage import S3StorageService
from video_service.infrastructure.adapters.output.messaging.sns_publisher import SNSEventPublisher

security = HTTPBearer()


async def get_video_repository(db=Depends(get_db)) -> IVideoRepository:
    return SQLAlchemyVideoRepository(db)


async def get_storage_service(
    settings: Annotated[Settings, Depends(get_settings)]
) -> IStorageService:
    return S3StorageService(
        bucket=settings.S3_BUCKET,
        endpoint_url=settings.AWS_ENDPOINT_URL or None,
        region=settings.AWS_DEFAULT_REGION,
    )


async def get_event_publisher(
    settings: Annotated[Settings, Depends(get_settings)]
) -> IEventPublisher:
    return SNSEventPublisher(
        topic_arn=settings.SNS_TOPIC_ARN,
        endpoint_url=settings.AWS_ENDPOINT_URL or None,
        region=settings.AWS_DEFAULT_REGION,
    )


async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> UUID:
    """Validate token with auth service and return user ID."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.AUTH_SERVICE_URL}/auth/me",
                headers={"Authorization": f"Bearer {credentials.credentials}"},
            )
            if response.status_code == 200:
                return UUID(response.json()["id"])
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except httpx.RequestError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Auth service unavailable")
