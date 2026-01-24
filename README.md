# 📹 Video Processor - Video Service

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Microserviço responsável pelo upload, listagem e gestão de vídeos.

## 📋 Índice

- [Arquitetura](#-arquitetura)
- [API Endpoints](#-api-endpoints)
- [Como Executar](#-como-executar)
- [Variáveis de Ambiente](#-variáveis-de-ambiente)
- [Testes](#-testes)

---

## 🏗️ Arquitetura

```
src/video_service/
├── domain/
│   └── entities/video.py        # Entidade Video
├── application/
│   ├── ports/output/            # IVideoRepository, IStorageService
│   └── use_cases/               # UploadVideo, GetVideo, ListVideos
└── infrastructure/
    ├── adapters/
    │   ├── input/api/           # FastAPI routes
    │   └── output/
    │       ├── persistence/     # SQLAlchemy repository
    │       ├── storage/         # S3 adapter
    │       └── messaging/       # SNS/SQS publishers
    └── config/                  # Settings
```

---

## 📡 API Endpoints

| Método | Endpoint | Descrição | Autenticação |
|--------|----------|-----------|--------------|
| POST | `/videos/upload` | Upload de vídeo | ✅ JWT |
| GET | `/videos` | Listar vídeos do usuário | ✅ JWT |
| GET | `/videos/{id}` | Detalhes do vídeo | ✅ JWT |
| DELETE | `/videos/{id}` | Deletar vídeo | ✅ JWT |
| GET | `/health` | Health check | ❌ |

### Exemplos

#### Upload de Vídeo

```bash
curl -X POST http://localhost:8002/videos/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@meu_video.mp4"
```

**Resposta:**
```json
{
  "id": "uuid",
  "filename": "meu_video.mp4",
  "size_bytes": 10485760,
  "status": "PENDING",
  "job_id": "uuid",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Listar Vídeos

```bash
curl http://localhost:8002/videos \
  -H "Authorization: Bearer $TOKEN"
```

**Resposta:**
```json
{
  "items": [
    {
      "id": "uuid",
      "filename": "video1.mp4",
      "status": "COMPLETED",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1
}
```

---

## 🚀 Como Executar

### Pré-requisitos

- Python 3.11+
- PostgreSQL
- AWS S3 (ou LocalStack)

### 1. Clone e instale

```bash
git clone https://github.com/morgadope/fiap-soat-video-service.git
cd fiap-soat-video-service
pip install -e ".[dev]"
```

### 2. Configure as variáveis

```bash
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5433/video_db"
export AWS_ENDPOINT_URL="http://localhost:4566"  # LocalStack
export S3_INPUT_BUCKET="video-uploads"
export SQS_JOB_QUEUE_URL="http://localhost:4566/000000000000/job-queue"
```

### 3. Execute

```bash
uvicorn video_service.infrastructure.adapters.input.api.main:app --reload --port 8002
```

---

## 🐳 Docker

```bash
docker build -t video-service .
docker run -p 8002:8002 \
  -e DATABASE_URL="..." \
  -e AWS_ENDPOINT_URL="..." \
  video-service
```

---

## ⚙️ Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `DATABASE_URL` | URL PostgreSQL | - |
| `AWS_ENDPOINT_URL` | Endpoint AWS/LocalStack | - |
| `S3_INPUT_BUCKET` | Bucket para uploads | video-uploads |
| `SQS_JOB_QUEUE_URL` | URL da fila de jobs | - |

---

## 🧪 Testes

```bash
pytest tests/ -v --cov=video_service
```

---

## 📄 Licença

MIT License
