"""FastAPI Application."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from video_service.infrastructure.adapters.input.api.routes import video_router, health_router
from video_service.infrastructure.adapters.output.persistence.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Video Service",
        description="Video management microservice",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(video_router, prefix="/videos", tags=["Videos"])
    app.mount("/metrics", make_asgi_app())

    return app


app = create_app()
