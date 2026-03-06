# Kubernetes - fiap-soat-video-service

Este diretorio contem os manifests para subir o `video-api-service` no Kubernetes, com autoscaling via `HorizontalPodAutoscaler` (CPU e memoria).

## Estrutura

- `base/`: manifests base reutilizaveis
- `overlays/local-dev/`: integracao com o ambiente `fiap-soat-video-local-dev` (PostgreSQL, Redis, LocalStack e Auth via Docker Compose)

## Pre-requisitos

- Cluster Kubernetes ativo
- `kubectl`
- `metrics-server` instalado no cluster (necessario para HPA baseado em CPU/memoria)

## Deploy local integrado com fiap-soat-video-local-dev

1. Suba a infraestrutura local (fora do cluster):

```bash
cd ../fiap-soat-video-local-dev
docker-compose -f docker-compose.infra.yml up -d
./init-scripts/localstack-init.sh
```

2. Faca build local da imagem (sem GHCR/ECR):

```bash
cd ..
docker build -t fiap-soat-video-service:local -f fiap-soat-video-service/Dockerfile .
```

3. Aplique os manifests do Video Service no cluster:

```bash
cd ../fiap-soat-video-service
kubectl apply -k k8s/overlays/local-dev
```

## Como funciona o HPA por CPU e memoria

- O recurso `HorizontalPodAutoscaler` (`video-api-service-hpa`) monitora o `Deployment/video-api-service`.
- Escala de `minReplicas: 1` ate `maxReplicas: 5`.
- Metricas:
  - CPU: `averageUtilization: 70`
  - Memoria: `averageUtilization: 75`

## Verificacao

```bash
kubectl get pods -n video-processor
kubectl get hpa -n video-processor
kubectl describe hpa video-api-service-hpa -n video-processor
```
