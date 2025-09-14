# Instruções Docker - API ML

## 🚀 Execução Rápida

### Opção 1: Docker Compose (Recomendado)

```bash
# A partir do diretório new_api/
cd new_api
docker-compose up --build

# Para executar em background
docker-compose up -d --build

# Para parar
docker-compose down
```

### Opção 2: Docker Manual

```bash
# A partir do diretório raiz do projeto
docker build -t ml-api .
docker run -p 3021:3021 --name ml-api-container ml-api

# Para parar
docker stop ml-api-container
docker rm ml-api-container
```

## 📋 Comandos Úteis

### Verificar Logs

```bash
# Com Docker Compose
docker-compose logs -f

# Com Docker manual
docker logs -f ml-api-container
```

### Executar Comandos no Container

```bash
# Com Docker Compose
docker-compose exec ml-api bash

# Com Docker manual
docker exec -it ml-api-container bash
```

### Verificar Status

```bash
# Verificar containers rodando
docker ps

# Verificar health check
docker inspect ml-api-container --format='{{.State.Health.Status}}'
```

## 🔧 Troubleshooting

### Problema: Modelos não encontrados

Certifique-se que a pasta `dist/` existe no diretório raiz do projeto com os modelos treinados.

### Problema: Porta já em uso

```bash
# Verificar o que está usando a porta 3021
lsof -i :3021

# Usar uma porta diferente
docker run -p 3022:3021 ml-api
```

### Problema: Build falha

```bash
# Limpar cache do Docker
docker system prune -a

# Rebuild sem cache
docker-compose build --no-cache
```

## 📊 Monitoramento

### Health Check

A API inclui health check automático que verifica:

- Status da aplicação
- Disponibilidade dos modelos
- Integridade do cache

### Logs Estruturados

Os logs incluem:

- Timestamp
- Nível de log
- Informações de requisição
- Métricas de performance

## 🔒 Segurança

### Usuário Não-Root

O container executa com usuário `appuser` para maior segurança.

### Network Isolation

O Docker Compose cria uma network isolada para os serviços.

### Resource Limits (Opcional)

Para limitar recursos, adicione ao `docker-compose.yml`:

```yaml
services:
  ml-api:
    # ... outras configurações
    deploy:
      resources:
        limits:
          cpus: "2.0"
          memory: 4G
        reservations:
          cpus: "1.0"
          memory: 2G
```

## 🚀 Deploy em Produção

### Variáveis de Ambiente

```bash
# Criar arquivo .env
echo "ENVIRONMENT=production" > .env
echo "LOG_LEVEL=INFO" >> .env

# Usar com Docker Compose
docker-compose --env-file .env up -d
```

### Nginx Reverse Proxy (Opcional)

```nginx
upstream ml-api {
    server 127.0.0.1:3021;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://ml-api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```
