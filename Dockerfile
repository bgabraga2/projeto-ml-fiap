# Dockerfile para API de Machine Learning - Projeto FIAP
FROM python:3.11-slim

# Definir variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Criar diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema necessárias para scikit-learn e outras libs
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro para aproveitar cache do Docker
COPY new_api/requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Criar estrutura de diretórios para artefatos versionados
RUN mkdir -p artefacts/v1/clusterization \
             artefacts/v1/classification \
             artefacts/v1/recommendation

# Copiar apenas os artefatos necessários para a API (modelos treinados)
COPY artefacts/v1/clusterization/ ./artefacts/v1/clusterization/
COPY artefacts/v1/classification/ ./artefacts/v1/classification/
COPY artefacts/v1/recommendation/ ./artefacts/v1/recommendation/

# Copiar código da aplicação
COPY new_api/main.py .
COPY new_api/test_api.py .
COPY new_api/README.md .

# Criar usuário não-root para segurança
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expor porta da aplicação
EXPOSE 3021

# Comando de saúde para verificar se a API está funcionando
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:3021/health')" || exit 1

# Comando para iniciar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3021", "--workers", "1"]
