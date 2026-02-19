import sys
import types
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


def _ensure_video_processor_shared_stubs() -> None:
    if "video_processor_shared" in sys.modules:
        return

    shared_module = types.ModuleType("video_processor_shared")
    domain_module = types.ModuleType("video_processor_shared.domain")
    events_module = types.ModuleType("video_processor_shared.domain.events")
    exceptions_module = types.ModuleType("video_processor_shared.domain.exceptions")

    class DomainEvent:
        event_type = "DomainEvent"

        def to_dict(self):
            return {}

    @dataclass
    class VideoUploadedEvent(DomainEvent):
        video_id: object
        user_id: object
        filename: str
        file_size: int
        event_type = "VideoUploaded"

        def to_dict(self):
            return {
                "video_id": str(self.video_id),
                "user_id": str(self.user_id),
                "filename": self.filename,
                "file_size": self.file_size,
            }

    class InvalidVideoFormatError(Exception):
        pass

    class VideoTooLargeError(Exception):
        pass

    class VideoNotFoundError(Exception):
        pass

    events_module.DomainEvent = DomainEvent
    events_module.VideoUploadedEvent = VideoUploadedEvent

    exceptions_module.InvalidVideoFormatError = InvalidVideoFormatError
    exceptions_module.VideoTooLargeError = VideoTooLargeError
    exceptions_module.VideoNotFoundError = VideoNotFoundError

    sys.modules["video_processor_shared"] = shared_module
    sys.modules["video_processor_shared.domain"] = domain_module
    sys.modules["video_processor_shared.domain.events"] = events_module
    sys.modules["video_processor_shared.domain.exceptions"] = exceptions_module


_ensure_video_processor_shared_stubs()
