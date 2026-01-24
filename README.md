# 📹 Video Processor - Video Service

Microserviço responsável pelo upload, listagem e gestão de vídeos.

## 📐 Arquitetura

```
fiap-soat-video-service/
├── src/video_service/
│   ├── domain/entities/          # Video entity
│   ├── application/
│   │   ├── ports/                # IVideoRepository, IStorageService
│   │   └── use_cases/            # UploadVideo, GetVideo, ListVideos
│   └── infrastructure/
│       ├── adapters/input/api/   # FastAPI routes
│       ├── adapters/output/      # PostgreSQL, S3 storage
│       └── config/               # Settings
├── Dockerfile
└── pyproject.toml
```

## 🚀 Rodar Localmente

### Pré-requisitos

- Python 3.11+
- PostgreSQL rodando na porta 5434
- MinIO/S3 na porta 9000

### 1. Clone e instale

```bash
git clone https://github.com/morgadope/fiap-soat-video-service.git
cd fiap-soat-video-service
pip install -e ".[dev]"
```

### 2. Configure variáveis de ambiente

```bash
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5434/video_db"
export AWS_ENDPOINT_URL="http://localhost:9000"
export AWS_ACCESS_KEY_ID="minioadmin"
export AWS_SECRET_ACCESS_KEY="minioadmin123"
export S3_BUCKET="video-processor"
```

### 3. Execute

```bash
uvicorn video_service.infrastructure.adapters.input.api.main:app --reload --port 8002
```

### 4. Acesse

- Swagger: http://localhost:8002/docs
- Health: http://localhost:8002/health

## 📖 API Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/videos/upload` | Upload de vídeo |
| GET | `/videos` | Listar vídeos do usuário |
| GET | `/videos/{video_id}` | Obter detalhes do vídeo |
| GET | `/health` | Health check |

### Exemplos

**Upload de vídeo:**
```bash
curl -X POST http://localhost:8002/videos/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@video.mp4"
```

**Listar vídeos:**
```bash
curl http://localhost:8002/videos \
  -H "Authorization: Bearer $TOKEN"
```

## 🐳 Docker

```bash
docker build -t video-service .
docker run -p 8002:8002 \
  -e DATABASE_URL=... \
  -e AWS_ENDPOINT_URL=... \
  video-service
```

## 🧪 Testes

```bash
pytest tests/ -v --cov=video_service
```

## 📄 Licença

MIT License
