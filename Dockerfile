# Video Service Dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Copy shared package first
COPY fiap-soat-video-shared/ /tmp/video-processor-shared/
RUN pip install --no-cache-dir /tmp/video-processor-shared/

COPY fiap-soat-video-service/pyproject.toml .
RUN pip install --no-cache-dir \
    "fastapi>=0.109.0" \
    "uvicorn[standard]>=0.27.0" \
    "prometheus-client>=0.20.0" \
    "pydantic>=2.0.0" \
    "pydantic-settings>=2.0.0" \
    "sqlalchemy>=2.0.0" \
    "asyncpg>=0.29.0" \
    "psycopg2-binary>=2.9.0" \
    "redis>=5.0.0" \
    "aioboto3>=12.0.0" \
    "python-multipart>=0.0.6" \
    "httpx>=0.26.0"

COPY fiap-soat-video-service/src/ src/

# Set Python path
ENV PYTHONPATH=/app/src

RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "video_service.infrastructure.adapters.input.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
