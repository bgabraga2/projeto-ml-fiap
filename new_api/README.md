# API de Machine Learning - Projeto FIAP

Esta API FastAPI serve três modelos de Machine Learning treinados para análise de dados de transporte:

1. **Clusterização de Clientes** - Segmentação comportamental usando K-Means
2. **Classificação de Recompra** - Predição de recompra em 30 dias
3. **Recomendação de Rotas** - Sistema de recomendação de rotas usando XGBoost

## 🚀 Como Iniciar

### Opção 1: Usando Docker (Recomendado)

#### Pré-requisitos

- Docker e Docker Compose instalados
- Modelos treinados na pasta `../dist/`

#### Execução com Docker Compose

```bash
# Executar a partir do diretório new_api/
docker-compose up --build
```

#### Execução com Docker (manual)

```bash
# Executar a partir do diretório raiz do projeto
docker build -t ml-api .
docker run -p 3021:3021 ml-api
```

### Opção 2: Execução Local (Python)

#### Pré-requisitos

- Python 3.8+
- Modelos treinados na pasta `../dist/`

#### Instalação e Execução

```bash
# Dar permissão de execução ao script
chmod +x start.sh

# Executar o script de inicialização
./start.sh
```

O script irá:

- Criar ambiente virtual
- Instalar dependências
- Verificar se os modelos existem
- Iniciar o servidor na porta 3021

### Acesso à Documentação

- **Swagger UI**: http://localhost:3021/docs
- **ReDoc**: http://localhost:3021/redoc

## 📋 Endpoints Disponíveis

### 1. Health Check

Verifica o status da API e dos modelos carregados.

**Endpoint:** `GET /health`

**Exemplo CURL:**

```bash
curl -X GET "http://localhost:3021/health" \
  -H "accept: application/json"
```

**Resposta de Exemplo:**

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.123456",
  "models": {
    "clusterization": true,
    "classification": true,
    "recommendation": true
  },
  "cache_status": {
    "loaded_models": ["clusterization", "classification", "recommendation"],
    "cache_size": 3
  }
}
```

---

### 2. Informações da API

Retorna informações básicas sobre a API.

**Endpoint:** `GET /`

**Exemplo CURL:**

```bash
curl -X GET "http://localhost:3021/" \
  -H "accept: application/json"
```

**Resposta de Exemplo:**

```json
{
  "message": "ML Models API",
  "version": "1.0.0",
  "endpoints": [
    "/clusterization - Segmentação de clientes",
    "/classification - Predição de recompra",
    "/recommendation - Recomendação de rotas"
  ]
}
```

---

### 3. Clusterização de Clientes

Segmenta clientes em clusters baseado no comportamento de compra.

**Endpoint:** `POST /clusterization`

**Parâmetros de Entrada:**

- `gmv_mean`: Valor médio das compras (GMV)
- `gmv_total`: Valor total das compras
- `purchase_count`: Número total de compras
- `gmv_std`: Desvio padrão do GMV
- `tickets_mean`: Média de tickets por compra
- `tickets_total`: Total de tickets comprados
- `tickets_std`: Desvio padrão dos tickets
- `round_trip_rate`: Taxa de viagens de ida e volta
- `weekend_rate`: Taxa de compras em fins de semana
- `preferred_day`: Dia da semana preferido (0-6)
- `avg_hour`: Hora média das compras
- `preferred_month`: Mês preferido (1-12)
- `avg_company_freq`: Frequência média da empresa

**Exemplo CURL:**

```bash
curl -X POST "http://localhost:3021/clusterization" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "gmv_mean": 112.86,
    "gmv_total": 1128.58,
    "purchase_count": 10,
    "gmv_std": 69.10,
    "tickets_mean": 1.0,
    "tickets_total": 10,
    "tickets_std": 0.0,
    "round_trip_rate": 1.0,
    "weekend_rate": 0.2,
    "preferred_day": 2,
    "avg_hour": 15.5,
    "preferred_month": 12,
    "avg_company_freq": 25000.0
  }'
```

**Resposta de Exemplo:**

```json
{
  "cluster": 0,
  "cluster_profile": {
    "description": "Clientes Regulares - Baixo Valor",
    "characteristics": {
      "gmv_mean": 143.12,
      "purchase_frequency": "Baixa-Média",
      "behavior": "Compras esporádicas, valores médios baixos"
    }
  },
  "confidence": 0.856
}
```

**Clusters Disponíveis:**

- **Cluster 0**: Clientes Regulares - Baixo Valor
- **Cluster 1**: Clientes Fins de Semana
- **Cluster 2**: Clientes Frequentes - Alto Valor
- **Cluster 3**: Clientes VIP - Altíssimo Volume
- **Cluster 4**: Clientes Premium - Tickets Múltiplos

---

### 4. Classificação de Recompra

Prediz se um cliente irá fazer uma recompra nos próximos 30 dias.

**Endpoint:** `POST /classification`

**Parâmetros de Entrada:**

- `gmv_ultima_compra`: GMV da última compra
- `tickets_ultima_compra`: Tickets da última compra
- `origem_ultima`: Hash da origem da última viagem
- `destino_ultima`: Hash do destino da última viagem
- `empresa_ultima`: Hash da empresa da última viagem
- `dias_desde_ultima_compra`: Dias desde a última compra
- `total_compras`: Total de compras históricas
- `dias_unicos_compra`: Dias únicos com compras
- `gmv_total`: GMV total histórico
- `gmv_medio`: GMV médio
- `gmv_std`: Desvio padrão do GMV
- `gmv_min`: GMV mínimo
- `gmv_max`: GMV máximo
- `tickets_total`: Total de tickets
- `tickets_medio`: Média de tickets
- `tickets_max`: Máximo de tickets
- `mes_preferido`: Mês preferido
- `dia_semana_preferido`: Dia da semana preferido
- `hora_media`: Hora média das compras
- `hora_std`: Desvio padrão da hora
- `origens_unicas`: Número de origens únicas
- `destinos_unicos`: Número de destinos únicos
- `empresas_unicas`: Número de empresas únicas
- `intervalo_medio_dias`: Intervalo médio entre compras
- `regularidade`: Regularidade das compras

**Exemplo CURL:**

```bash
curl -X POST "http://localhost:3021/classification" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "gmv_ultima_compra": 79.52,
    "tickets_ultima_compra": 1,
    "origem_ultima": "10e4e7caf8b078429bb1c80b1a10118ac6f963eff098fd",
    "destino_ultima": "e6d41d208672a4e50b86d959f4a6254975e6fb9b088116",
    "empresa_ultima": "36ebe205bcdfc499a25e6923f4450fa8d48196ceb4fa0c",
    "dias_desde_ultima_compra": 666,
    "total_compras": 2,
    "dias_unicos_compra": 2,
    "gmv_total": 162.0,
    "gmv_medio": 81.0,
    "gmv_std": 2.24,
    "gmv_min": 79.52,
    "gmv_max": 82.48,
    "tickets_total": 2,
    "tickets_medio": 1.0,
    "tickets_max": 1,
    "mes_preferido": 5,
    "dia_semana_preferido": 2,
    "hora_media": 15.1,
    "hora_std": 0.0,
    "origens_unicas": 2,
    "destinos_unicos": 2,
    "empresas_unicas": 2,
    "intervalo_medio_dias": 487.0,
    "regularidade": 0.0
  }'
```

**Resposta de Exemplo:**

```json
{
  "will_purchase": false,
  "probability": 0.15,
  "risk_category": "Baixo"
}
```

**Categorias de Risco:**

- **Alto** (≥60%): Cliente muito provável de comprar - ofertas premium
- **Médio** (30-59%): Cliente moderado - campanhas direcionadas
- **Baixo** (<30%): Cliente improvável - campanhas de reativação

---

### 5. Recomendação de Rotas

Recomenda as 3 melhores rotas baseado no perfil e histórico do cliente.

**Endpoint:** `POST /recommendation`

**Parâmetros de Entrada:**

- `fk_contact`: ID do contato (hash)
- `date_purchase`: Data da compra (YYYY-MM-DD)
- `time_purchase`: Hora da compra (HH:MM:SS)
- `place_origin_departure`: Local de origem (hash)
- `place_destination_departure`: Local de destino (hash)
- `place_origin_return`: Local de origem do retorno (hash)
- `place_destination_return`: Local de destino do retorno (hash)
- `fk_departure_ota_bus_company`: Empresa de ônibus (hash)
- `fk_return_ota_bus_company`: Empresa de ônibus retorno (hash)
- `gmv_success`: GMV da transação
- `total_tickets_quantity_success`: Quantidade de tickets
- `route_departure`: Rota de ida (hash)
- `route_return`: Rota de volta (hash)
- `is_round_trip`: Viagem de ida e volta (0 ou 1)
- `departure_company_freq`: Frequência da empresa
- `return_company_freq`: Frequência da empresa retorno
- `origin_dept_freq`: Frequência da origem
- `dest_dept_freq`: Frequência do destino
- `route_departure_freq`: Frequência da rota
- `cluster`: Cluster do cliente

**Exemplo CURL:**

```bash
curl -X POST "http://localhost:3021/recommendation" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "fk_contact": "37228485e0dc83d84d1bcd1bef3dc632301bf6cb22c8b5",
    "date_purchase": "2018-12-05",
    "time_purchase": "15:07:57",
    "place_origin_departure": "10e4e7caf8b078429bb1c80b1a10118ac6f963eff098fd25a66c78862ae5ebce",
    "place_destination_departure": "e6d41d208672a4e50b86d959f4a6254975e6fb9b0881166af52c9fe3b5825de2",
    "place_origin_return": "0",
    "place_destination_return": "0",
    "fk_departure_ota_bus_company": "36ebe205bcdfc499a25e6923f4450fa8d48196ceb4fa0ce077d9d8ec4a36926d",
    "fk_return_ota_bus_company": "1",
    "gmv_success": 155.97,
    "total_tickets_quantity_success": 1,
    "route_departure": "10e4e7caf8b078429bb1c80b1a10118ac6f963eff098fd25a66c78862ae5ebce_to_e6d41d208672a4e50b86d959f4a6254975e6fb9b0881166af52c9fe3b5825de2",
    "route_return": "0_to_0",
    "is_round_trip": 1,
    "departure_company_freq": 2139,
    "return_company_freq": 1548675,
    "origin_dept_freq": 862,
    "dest_dept_freq": 5,
    "route_departure_freq": 1,
    "cluster": 0
  }'
```

**Resposta de Exemplo:**

```json
{
  "top_3_routes": [
    {
      "rank": 1,
      "route": "route_abc_to_def",
      "probability": 0.85,
      "confidence": 85.0
    },
    {
      "rank": 2,
      "route": "route_ghi_to_jkl",
      "probability": 0.72,
      "confidence": 72.0
    },
    {
      "rank": 3,
      "route": "route_mno_to_pqr",
      "probability": 0.68,
      "confidence": 68.0
    }
  ],
  "user_cluster": 0
}
```

---

## 🧪 Testando a API

Execute o script de teste para verificar todos os endpoints:

```bash
python test_api.py
```

O script de teste utiliza dados reais extraídos dos datasets dos modelos treinados e testa:

- Health check
- Todos os endpoints de predição
- Casos extremos com diferentes perfis de cliente

## 🔧 Estrutura do Projeto

```
new_api/
├── main.py           # Código principal da API
├── test_api.py       # Script de teste com dados reais
├── start.sh          # Script de inicialização
├── requirements.txt  # Dependências Python
├── README.md         # Este arquivo
└── venv/            # Ambiente virtual
```

## 📊 Modelos Utilizados

### Clusterização (K-Means)

- **Objetivo**: Segmentar clientes por comportamento de compra
- **Features**: GMV, frequência, padrões temporais
- **Clusters**: 5 segmentos distintos de clientes

### Classificação (Modelo Supervisionado)

- **Objetivo**: Predizer recompra em 30 dias
- **Features**: Histórico de compras, padrões comportamentais
- **Output**: Probabilidade + categoria de risco

### Recomendação (XGBoost)

- **Objetivo**: Recomendar rotas baseado no perfil
- **Features**: Histórico, preferências, cluster, contexto temporal
- **Output**: Top 3 rotas mais prováveis

## 🚨 Tratamento de Erros

A API implementa tratamento robusto de erros:

- **Validação de entrada** com Pydantic
- **Tratamento defensivo** para valores não vistos no treinamento
- **Cache de modelos** para performance
- **Logs detalhados** para debugging

## 📈 Performance

- **Cache de modelos**: Evita recarregamento a cada requisição
- **Lazy loading**: Modelos carregados sob demanda
- **Warm-up**: Pré-carregamento opcional na inicialização
- **Validação rápida**: Health check para monitoramento

## 🔒 Considerações de Segurança

- Todos os dados sensíveis são hasheados nos exemplos
- Validação rigorosa de entrada
- Tratamento seguro de exceções
- Logs sem exposição de dados sensíveis

## 🐳 Vantagens do Docker

### Benefícios da Containerização

- **Portabilidade**: Funciona em qualquer ambiente com Docker
- **Isolamento**: Dependências isoladas do sistema host
- **Reproducibilidade**: Ambiente consistente entre desenvolvimento e produção
- **Facilidade de deploy**: Deploy simplificado em qualquer servidor
- **Escalabilidade**: Fácil de escalar horizontalmente
- **Segurança**: Execução com usuário não-root no container

### Recursos Docker Implementados

- **Multi-stage build**: Otimização de tamanho da imagem
- **Health check**: Monitoramento automático da saúde da aplicação
- **Usuário não-root**: Execução segura no container
- **Docker Compose**: Orquestração simplificada
- **Volume de logs**: Persistência de logs fora do container
- **Network isolada**: Comunicação segura entre serviços

---

**Desenvolvido para o Projeto ML FIAP - 2024**
