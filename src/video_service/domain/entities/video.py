"""Video Entity."""
from datetime import UTC, datetime
from typing import Optional
from uuid import UUID


class Video:
    """Video Entity - Represents an uploaded video."""

    ALLOWED_FORMATS = ['mp4', 'avi', 'mov', 'mkv', 'webm']
    MAX_SIZE_MB = 500

    def __init__(
        self,
        id: UUID,
        user_id: UUID,
        original_filename: str,
        file_path: str,
        file_size: int,
        format: str,
        duration: Optional[float] = None,
        created_at: Optional[datetime] = None
    ):
        self.id = id
        self.user_id = user_id
        self.original_filename = original_filename
        self.file_path = file_path
        self.file_size = file_size
        self.format = format.lower()
        self.duration = duration
        self.created_at = created_at or datetime.now(UTC)

    @property
    def file_size_mb(self) -> float:
        return self.file_size / (1024 * 1024)

    @property
    def is_valid_format(self) -> bool:
        return self.format in self.ALLOWED_FORMATS

    @property
    def is_valid_size(self) -> bool:
        return self.file_size_mb <= self.MAX_SIZE_MB

    def set_duration(self, duration: float) -> None:
        self.duration = duration

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Video):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
