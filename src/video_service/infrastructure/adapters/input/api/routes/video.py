"""Video API Routes."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, File, UploadFile, HTTPException, status, Depends, Query

from video_service.application.use_cases import UploadVideoUseCase, GetVideoUseCase, ListVideosUseCase
from video_service.application.use_cases.upload_video import UploadVideoInput
from video_service.infrastructure.adapters.input.api.schemas.video import VideoResponse, PaginatedVideoResponse
from video_service.infrastructure.adapters.input.api.dependencies import (
    get_video_repository,
    get_storage_service,
    get_event_publisher,
    get_current_user_id,
)

from video_processor_shared.domain.exceptions import InvalidVideoFormatError, VideoTooLargeError, VideoNotFoundError

router = APIRouter()


@router.post("/upload", response_model=VideoResponse, status_code=status.HTTP_201_CREATED)
async def upload_video(
    file: Annotated[UploadFile, File()],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    video_repository=Depends(get_video_repository),
    storage_service=Depends(get_storage_service),
    event_publisher=Depends(get_event_publisher),
):
    """Upload a video file."""
    try:
        # Get file size
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)

        use_case = UploadVideoUseCase(
            video_repository=video_repository,
            storage_service=storage_service,
            event_publisher=event_publisher,
        )

        result = await use_case.execute(
            UploadVideoInput(
                user_id=user_id,
                filename=file.filename,
                file=file.file,
                file_size=file_size,
                content_type=file.content_type or "video/mp4",
            )
        )

        return VideoResponse(
            id=result.id,
            user_id=result.user_id,
            original_filename=result.original_filename,
            file_size=result.file_size,
            format=result.format,
            created_at=result.created_at,
        )
    except InvalidVideoFormatError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except VideoTooLargeError as e:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=str(e))


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    video_repository=Depends(get_video_repository),
):
    """Get video by ID."""
    try:
        use_case = GetVideoUseCase(video_repository=video_repository)
        result = await use_case.execute(video_id, user_id)
        return VideoResponse(
            id=result.id,
            user_id=result.user_id,
            original_filename=result.original_filename,
            file_size=result.file_size,
            format=result.format,
            created_at=result.created_at,
        )
    except VideoNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")


@router.get("/", response_model=PaginatedVideoResponse)
async def list_videos(
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
    video_repository=Depends(get_video_repository),
):
    """List user's videos."""
    use_case = ListVideosUseCase(video_repository=video_repository)
    result = await use_case.execute(user_id, page, page_size)
    return PaginatedVideoResponse(
        videos=[
            VideoResponse(
                id=v.id,
                user_id=v.user_id,
                original_filename=v.original_filename,
                file_size=v.file_size,
                format=v.format,
                created_at=v.created_at,
            )
            for v in result.videos
        ],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
    )
