"""API Routes."""
from video_service.infrastructure.adapters.input.api.routes.video import router as video_router
from video_service.infrastructure.adapters.input.api.routes.health import router as health_router

__all__ = ["video_router", "health_router"]
