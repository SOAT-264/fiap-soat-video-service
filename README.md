# fiap-soat-video-service

## Introdução
> Este repositório faz parte do projeto [FIAP SOAT Video Processor](https://github.com/SOAT-264/fiap-soat-video-local-dev).

Microserviço responsável por upload e gerenciamento de vídeos. Ele valida autenticação com o serviço de auth, persiste metadados e publica eventos de domínio para iniciar o pipeline assíncrono de processamento.

## Sumário
- Explicação do projeto
- Objetivo
- Como funciona
- Repositórios relacionados
- Integrações com outros repositórios
- Como executar
- Como testar

## Repositórios relacionados
- [fiap-soat-video-auth](https://github.com/SOAT-264/fiap-soat-video-auth)
- [fiap-soat-video-jobs](https://github.com/SOAT-264/fiap-soat-video-jobs)
- [fiap-soat-video-shared](https://github.com/SOAT-264/fiap-soat-video-shared)
- [fiap-soat-video-local-dev](https://github.com/SOAT-264/fiap-soat-video-local-dev)
- [fiap-soat-video-obs](https://github.com/SOAT-264/fiap-soat-video-obs)

## Explicação do projeto
O projeto implementa API FastAPI para operações de vídeo e segue arquitetura em camadas (`application`, `domain`, `infrastructure`). O upload utiliza storage S3 compatível e publica eventos para o fluxo de jobs.

## Objetivo
Centralizar a entrada de vídeos na plataforma, garantindo controle de acesso, persistência e disparo confiável do processamento assíncrono.

## Como funciona
1. `POST /videos/upload` recebe um ou mais arquivos de vídeo autenticados.
2. O token bearer é validado em `fiap-soat-video-auth` via `GET /auth/me`.
3. O arquivo é enviado para S3 (`video-uploads`) e o metadado é salvo no banco.
4. O caso de uso publica `VideoUploadedEvent` via SNS (`video-events`).
5. Endpoints de consulta:
`GET /videos/{video_id}`, `GET /videos`, além de `GET /health` e `GET /metrics`.

## Integrações com outros repositórios
| Repositório integrado | Como integra | Para que serve |
| --- | --- | --- |
| `fiap-soat-video-auth` | Chamada HTTP para `GET /auth/me` durante requests autenticadas | Validar identidade do usuário antes de permitir upload/consulta |
| `fiap-soat-video-jobs` | Publicação de evento `video-events` (SNS) consumido pelo worker de jobs via SQS | Iniciar processamento assíncrono do vídeo enviado |
| `fiap-soat-video-notifications` | Integração indireta via pipeline de eventos (`job-events`) após processamento | Notificar usuário ao final ou falha de processamento |
| `fiap-soat-video-shared` | Uso de eventos/exceções compartilhadas (`VideoUploadedEvent`, erros de domínio) | Padronizar contrato de domínio entre serviços |
| `fiap-soat-video-local-dev` | Infra local (DB/Redis/LocalStack), deploy em k8s local-dev e rota `video.localhost` | Executar fluxo completo ponta a ponta no ambiente principal |
| `fiap-soat-video-obs` | Exposição de `/health` e `/metrics` para scraping | Monitorar saúde e métricas da API de vídeo |

## Como executar
### Pré-requisitos
- Python 3.11+
- Infra local (recomendado via `fiap-soat-video-local-dev`)

### Execução local da API
```powershell
cd /fiap-soat-video-service
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"

$env:DATABASE_URL="postgresql+asyncpg://postgres:postgres123@localhost:5433/video_db"
$env:REDIS_URL="redis://localhost:6379/1"
$env:AWS_ENDPOINT_URL="http://localhost:4566"
$env:AWS_ACCESS_KEY_ID="test"
$env:AWS_SECRET_ACCESS_KEY="test"
$env:AWS_DEFAULT_REGION="us-east-1"
$env:S3_BUCKET="video-uploads"
$env:SNS_TOPIC_ARN="arn:aws:sns:us-east-1:000000000000:video-events"
$env:AUTH_SERVICE_URL="http://localhost:8001"

uvicorn video_service.infrastructure.adapters.input.api.main:app --host 0.0.0.0 --port 8002 --reload
```

### Execução integrada (recomendada)
```powershell
cd /fiap-soat-video-local-dev
.\start.ps1
```

## Como testar
```powershell
cd /fiap-soat-video-service
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest
```


