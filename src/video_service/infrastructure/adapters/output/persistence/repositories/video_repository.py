"""SQLAlchemy Video Repository."""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from video_service.domain.entities.video import Video
from video_service.application.ports.output.repositories.video_repository import IVideoRepository
from video_service.infrastructure.adapters.output.persistence.models import VideoModel


class SQLAlchemyVideoRepository(IVideoRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, video: Video) -> Video:
        model = VideoModel(
            id=video.id,
            user_id=video.user_id,
            original_filename=video.original_filename,
            file_path=video.file_path,
            file_size=video.file_size,
            format=video.format,
            duration=video.duration,
            created_at=video.created_at,
        )
        self._session.add(model)
        await self._session.flush()
        return video

    async def find_by_id(self, video_id: UUID) -> Optional[Video]:
        stmt = select(VideoModel).where(VideoModel.id == video_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def find_by_user_id(self, user_id: UUID, skip: int = 0, limit: int = 10) -> List[Video]:
        stmt = (
            select(VideoModel)
            .where(VideoModel.user_id == user_id)
            .order_by(VideoModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def delete(self, video_id: UUID) -> bool:
        stmt = select(VideoModel).where(VideoModel.id == video_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False

    async def count_by_user_id(self, user_id: UUID) -> int:
        stmt = select(func.count()).where(VideoModel.user_id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    def _to_entity(self, model: VideoModel) -> Video:
        return Video(
            id=model.id,
            user_id=model.user_id,
            original_filename=model.original_filename,
            file_path=model.file_path,
            file_size=model.file_size,
            format=model.format,
            duration=model.duration,
            created_at=model.created_at,
        )
