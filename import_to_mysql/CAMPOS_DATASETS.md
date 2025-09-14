# Documentação dos Campos dos Datasets ML

Este documento descreve detalhadamente todos os campos dos três datasets de Machine Learning importados para o MySQL.

## Visão Geral dos Datasets

Os três datasets representam diferentes modelos de ML aplicados aos dados de vendas de passagens:

1. **ml_classification** - Predição de recompra de clientes (572K registros)
2. **ml_clusterization** - Segmentação de clientes por comportamento (1.7M registros)
3. **ml_recommendation** - Recomendação de próximas rotas (46K registros)

---

## 1. Dataset de Classificação (`ml_classification`)

**Propósito**: Predizer a probabilidade de um cliente fazer uma nova compra nos próximos 30 dias.

### Campos de Identificação

| Campo        | Tipo         | Descrição                                 |
| ------------ | ------------ | ----------------------------------------- |
| `id`         | BIGINT       | Chave primária auto-incremento            |
| `fk_contact` | VARCHAR(255) | **Identificador único do cliente** (hash) |

### Campos de Target e Predição

| Campo                  | Tipo          | Descrição                                                             |
| ---------------------- | ------------- | --------------------------------------------------------------------- |
| `target`               | TINYINT(1)    | **Variável alvo**: 0=não recomprou, 1=recomprou nos 30 dias seguintes |
| `probabilidade_compra` | DECIMAL(10,6) | **Probabilidade predita** de recompra (0.0 a 1.0)                     |
| `predicao_compra`      | TINYINT(1)    | **Predição binária**: 0=não vai recomprar, 1=vai recomprar            |
| `potencial_recompra`   | ENUM          | **Categoria de risco**: 'Baixo', 'Médio', 'Alto', 'Muito Alto'        |

### Campos de Comportamento de Compra (Features RFM)

| Campo                      | Tipo          | Descrição                                             |
| -------------------------- | ------------- | ----------------------------------------------------- |
| `data_ultima_compra`       | DATE          | Data da última compra do cliente                      |
| `dias_desde_ultima_compra` | INT           | **Recency**: Número de dias desde a última compra     |
| `total_compras`            | INT           | **Frequency**: Total de compras históricas do cliente |
| `gmv_ultima_compra`        | DECIMAL(10,2) | Valor (GMV) da última compra                          |
| `gmv_total`                | DECIMAL(12,2) | **Monetary**: Valor total gasto pelo cliente          |
| `gmv_medio`                | DECIMAL(10,2) | Valor médio por compra                                |
| `tickets_ultima_compra`    | INT           | Quantidade de tickets na última compra                |

### Campos Temporais

| Campo               | Tipo    | Descrição                   |
| ------------------- | ------- | --------------------------- |
| `mes_ultima_compra` | TINYINT | Mês da última compra (1-12) |
| `ano_ultima_compra` | YEAR    | Ano da última compra        |

### Campos de Diversidade Comportamental

| Campo             | Tipo | Descrição                                              |
| ----------------- | ---- | ------------------------------------------------------ |
| `origens_unicas`  | INT  | Quantidade de origens diferentes utilizadas            |
| `destinos_unicos` | INT  | Quantidade de destinos diferentes utilizados           |
| `empresas_unicas` | INT  | Quantidade de empresas de ônibus diferentes utilizadas |

### Campos de Regularidade

| Campo                  | Tipo          | Descrição                                          |
| ---------------------- | ------------- | -------------------------------------------------- |
| `intervalo_medio_dias` | DECIMAL(10,2) | Intervalo médio em dias entre compras              |
| `regularidade`         | DECIMAL(10,2) | Métrica de regularidade do comportamento de compra |

### Campos de Controle

| Campo           | Tipo        | Descrição                                            |
| --------------- | ----------- | ---------------------------------------------------- |
| `data_predicao` | DATETIME    | Timestamp da predição                                |
| `versao_modelo` | VARCHAR(50) | Versão do modelo utilizado (ex: "RandomForest_v1.0") |
| `created_at`    | TIMESTAMP   | Data de inserção no banco                            |

---

## 2. Dataset de Clusterização (`ml_clusterization`)

**Propósito**: Segmentar clientes em grupos comportamentais usando K-Means clustering.

### Campos de Identificação

| Campo                 | Tipo         | Descrição                           |
| --------------------- | ------------ | ----------------------------------- |
| `id`                  | BIGINT       | Chave primária auto-incremento      |
| `nk_ota_localizer_id` | VARCHAR(255) | **Identificador da transação**      |
| `fk_contact`          | VARCHAR(255) | **Identificador do cliente** (hash) |

### Campos Temporais da Transação

| Campo           | Tipo        | Descrição                                               |
| --------------- | ----------- | ------------------------------------------------------- |
| `date_purchase` | DATE        | **Data da compra**                                      |
| `time_purchase` | TIME        | **Hora da compra**                                      |
| `day_of_week`   | TINYINT     | Dia da semana (0=domingo, 6=sábado)                     |
| `month`         | TINYINT     | Mês da compra (1-12)                                    |
| `quarter`       | TINYINT     | Trimestre da compra (1-4)                               |
| `is_weekend`    | TINYINT(1)  | Se a compra foi no fim de semana (0=não, 1=sim)         |
| `hour`          | TINYINT     | Hora da compra (0-23)                                   |
| `period_of_day` | VARCHAR(20) | Período do dia ('Manhã', 'Tarde', 'Noite', 'Madrugada') |

### Campos de Rota e Localização

| Campo                         | Tipo         | Descrição                                   |
| ----------------------------- | ------------ | ------------------------------------------- |
| `place_origin_departure`      | VARCHAR(255) | **Local de origem** da viagem de ida        |
| `place_destination_departure` | VARCHAR(255) | **Local de destino** da viagem de ida       |
| `place_origin_return`         | VARCHAR(255) | Local de origem da viagem de volta          |
| `place_destination_return`    | VARCHAR(255) | Local de destino da viagem de volta         |
| `route_departure`             | TEXT         | **Rota completa de ida** (origem → destino) |
| `route_return`                | TEXT         | Rota completa de volta                      |
| `is_round_trip`               | TINYINT(1)   | Se é viagem de ida e volta (0=não, 1=sim)   |

### Campos de Empresa e Transação

| Campo                            | Tipo          | Descrição                                              |
| -------------------------------- | ------------- | ------------------------------------------------------ |
| `fk_departure_ota_bus_company`   | VARCHAR(255)  | **Empresa de ônibus** da viagem de ida                 |
| `fk_return_ota_bus_company`      | VARCHAR(255)  | Empresa de ônibus da viagem de volta                   |
| `gmv_success`                    | DECIMAL(10,2) | **Valor da transação** (GMV = Gross Merchandise Value) |
| `total_tickets_quantity_success` | INT           | **Quantidade de tickets** comprados                    |

### Campos de Frequência e Popularidade

| Campo                    | Tipo | Descrição                                   |
| ------------------------ | ---- | ------------------------------------------- |
| `departure_company_freq` | INT  | **Frequência da empresa** de ida no dataset |
| `return_company_freq`    | INT  | Frequência da empresa de volta no dataset   |
| `origin_dept_freq`       | INT  | **Frequência da origem** no dataset         |
| `dest_dept_freq`         | INT  | **Frequência do destino** no dataset        |
| `route_departure_freq`   | INT  | **Frequência da rota** no dataset           |

### Campos de Clustering

| Campo                | Tipo        | Descrição                                          |
| -------------------- | ----------- | -------------------------------------------------- |
| `cluster`            | TINYINT     | **Cluster atribuído** pelo algoritmo K-Means (0-4) |
| `data_clusterizacao` | DATETIME    | Timestamp da clusterização                         |
| `versao_modelo`      | VARCHAR(50) | Versão do modelo de clustering                     |
| `created_at`         | TIMESTAMP   | Data de inserção no banco                          |

---

## 3. Dataset de Recomendação (`ml_recommendation`) - SCHEMA SIMPLIFICADO

**Propósito**: Armazenar as recomendações de próximas rotas geradas pelo modelo XGBoost.

**Observação**: Esta tabela contém apenas os dados essenciais de recomendação. Para análises mais complexas que requerem dados completos de clusterização, utilize JOINs com a tabela `ml_clusterization`.

### Campos de Identificação

| Campo                 | Tipo         | Descrição                                 |
| --------------------- | ------------ | ----------------------------------------- |
| `id`                  | BIGINT       | Chave primária auto-incremento            |
| `nk_ota_localizer_id` | VARCHAR(255) | **Identificador da transação**            |
| `fk_contact`          | VARCHAR(255) | **Identificador único do cliente** (hash) |

### Campos de Contexto

| Campo             | Tipo | Descrição                            |
| ----------------- | ---- | ------------------------------------ |
| `date_purchase`   | DATE | **Data da compra** original          |
| `route_departure` | TEXT | **Rota atual** do cliente (contexto) |

### Campos de Recomendação

| Campo               | Tipo | Descrição                                     |
| ------------------- | ---- | --------------------------------------------- |
| `predicted_route_1` | TEXT | **1ª rota recomendada** (maior probabilidade) |
| `predicted_route_2` | TEXT | **2ª rota recomendada**                       |
| `predicted_route_3` | TEXT | **3ª rota recomendada**                       |
| `predicted_route_4` | TEXT | **4ª rota recomendada**                       |
| `predicted_route_5` | TEXT | **5ª rota recomendada**                       |

### Campos de Probabilidade

| Campo          | Tipo          | Descrição                                        |
| -------------- | ------------- | ------------------------------------------------ |
| `prob_route_1` | DECIMAL(10,6) | **Probabilidade da 1ª recomendação** (0.0 a 1.0) |
| `prob_route_2` | DECIMAL(10,6) | **Probabilidade da 2ª recomendação**             |
| `prob_route_3` | DECIMAL(10,6) | **Probabilidade da 3ª recomendação**             |
| `prob_route_4` | DECIMAL(10,6) | **Probabilidade da 4ª recomendação**             |
| `prob_route_5` | DECIMAL(10,6) | **Probabilidade da 5ª recomendação**             |

### Campos de Controle

| Campo        | Tipo      | Descrição                 |
| ------------ | --------- | ------------------------- |
| `created_at` | TIMESTAMP | Data de inserção no banco |

---

## Índices e Performance

### ml_classification

- `idx_fk_contact` - Consultas por cliente
- `idx_potencial` - Filtros por categoria de risco
- `idx_probabilidade` - Ordenação por probabilidade
- `idx_target` - Análises de performance do modelo

### ml_clusterization

- `idx_fk_contact` - Consultas por cliente
- `idx_cluster` - Análises por segmento
- `idx_date_purchase` - Filtros temporais
- `idx_route_departure` - Consultas por rota

### ml_recommendation (Schema Simplificado)

- `idx_fk_contact` - Consultas por cliente
- `idx_date_purchase` - Filtros temporais
- `idx_route_departure` - Consultas por rota atual (contexto)
- `idx_predicted_route_1` - Consultas por recomendação principal

**Nota**: Para análises que requerem dados de cluster, faça JOIN com `ml_clusterization`.

---

## Relacionamentos entre Datasets

### Cliente (`fk_contact`)

- **Presente em todos os 3 datasets**
- Permite análise integrada do comportamento do cliente
- Hash para preservar privacidade

### Cluster

- **Gerado no dataset de clusterização**
- **Utilizado no dataset de recomendação**
- Permite recomendações baseadas no perfil comportamental

### Temporal

- **Sequência temporal** permite análise de evolução do comportamento
- **Sazonalidade** identificada através dos campos de data/hora

---

## Observações Técnicas

1. **Encoding**: Todos os textos estão em UTF-8 para suportar caracteres especiais
2. **Precisão**: Probabilidades com 6 casas decimais para máxima precisão
3. **Performance**: Índices otimizados para consultas típicas de ML
4. **Escalabilidade**: Estrutura preparada para crescimento dos dados
5. **Auditoria**: Campos de controle para rastreabilidade das predições
