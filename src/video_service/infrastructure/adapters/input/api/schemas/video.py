"""Video Schemas."""
from datetime import datetime
from typing import List
from uuid import UUID
from pydantic import ConfigDict, BaseModel


class VideoResponse(BaseModel):
    id: UUID
    user_id: UUID
    original_filename: str
    file_size: int
    format: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PaginatedVideoResponse(BaseModel):
    videos: List[VideoResponse]
    total: int
    page: int
    page_size: int
