-- =====================================================
-- Índices de Otimização para Tabelas ML
-- Projeto ML FIAP - Otimização de Performance do Banco
-- =====================================================

-- Este script cria índices adicionais para otimizar as consultas mais comuns
-- nas tabelas de Machine Learning já criadas pelo script load_ml_datasets_to_mysql.py

-- =====================================================
-- ANÁLISE DOS ÍNDICES EXISTENTES
-- =====================================================

-- ml_classification já possui:
-- - idx_fk_contact (fk_contact)
-- - idx_potencial (potencial_recompra) 
-- - idx_probabilidade (probabilidade_compra)
-- - idx_target (target)

-- ml_clusterization já possui:
-- - idx_fk_contact (fk_contact)
-- - idx_cluster (cluster)
-- - idx_date_purchase (date_purchase)
-- - idx_route_departure (route_departure(100))

-- ml_recommendation já possui:
-- - idx_fk_contact (fk_contact)
-- - idx_date_purchase (date_purchase)
-- - idx_route_departure (route_departure(100))
-- - idx_predicted_route_1 (predicted_route_1(100))

-- =====================================================
-- ÍNDICES ADICIONAIS PARA ml_classification
-- =====================================================

-- Índices compostos para consultas de segmentação e análise
CREATE INDEX idx_classification_potencial_prob ON ml_classification (potencial_recompra, probabilidade_compra DESC);

CREATE INDEX idx_classification_target_prob ON ml_classification (target, probabilidade_compra DESC);

-- Índices para análise temporal
CREATE INDEX idx_classification_data_ultima ON ml_classification (data_ultima_compra);

CREATE INDEX idx_classification_mes_ano ON ml_classification (ano_ultima_compra, mes_ultima_compra);

-- Índices para análise comportamental (RFM)
CREATE INDEX idx_classification_gmv_total ON ml_classification (gmv_total DESC);

CREATE INDEX idx_classification_total_compras ON ml_classification (total_compras DESC);

CREATE INDEX idx_classification_dias_ultima ON ml_classification (dias_desde_ultima_compra);

-- Índice composto para análise RFM completa
CREATE INDEX idx_classification_rfm ON ml_classification (dias_desde_ultima_compra, total_compras, gmv_total);

-- Índices para análise de diversidade
CREATE INDEX idx_classification_diversidade ON ml_classification (origens_unicas, destinos_unicos, empresas_unicas);

-- Índice para análise de regularidade
CREATE INDEX idx_classification_regularidade ON ml_classification (regularidade, intervalo_medio_dias);

-- Índice para consultas por data de predição
CREATE INDEX idx_classification_data_predicao ON ml_classification (data_predicao);

-- Índice para consultas por versão do modelo
CREATE INDEX idx_classification_versao ON ml_classification (versao_modelo);

-- Índice composto para campanhas de marketing (alto potencial + alto valor)
CREATE INDEX idx_classification_campanha ON ml_classification (potencial_recompra, gmv_total DESC, probabilidade_compra DESC);

-- =====================================================
-- ÍNDICES ADICIONAIS PARA ml_clusterization  
-- =====================================================

-- Índices compostos para análise de clusters
CREATE INDEX idx_clusterization_cluster_gmv ON ml_clusterization (cluster, gmv_success DESC);

CREATE INDEX idx_clusterization_cluster_date ON ml_clusterization (cluster, date_purchase);

-- Índices para análise temporal
CREATE INDEX idx_clusterization_temporal ON ml_clusterization (month, day_of_week, hour);

CREATE INDEX idx_clusterization_weekend ON ml_clusterization (is_weekend, period_of_day);

-- Índices para análise de localização
CREATE INDEX idx_clusterization_origem ON ml_clusterization (place_origin_departure);

CREATE INDEX idx_clusterization_destino ON ml_clusterization (place_destination_departure);

CREATE INDEX idx_clusterization_origem_destino ON ml_clusterization (place_origin_departure, place_destination_departure);

-- Índices para análise de empresas
CREATE INDEX idx_clusterization_empresa_ida ON ml_clusterization (fk_departure_ota_bus_company);

CREATE INDEX idx_clusterization_empresa_volta ON ml_clusterization (fk_return_ota_bus_company);

-- Índices para análise de viagem
CREATE INDEX idx_clusterization_round_trip ON ml_clusterization (is_round_trip);

CREATE INDEX idx_clusterization_tickets ON ml_clusterization (total_tickets_quantity_success DESC);

-- Índices para análise de frequência
CREATE INDEX idx_clusterization_freq_empresa ON ml_clusterization (departure_company_freq DESC);

CREATE INDEX idx_clusterization_freq_origem ON ml_clusterization (origin_dept_freq DESC);

CREATE INDEX idx_clusterization_freq_destino ON ml_clusterization (dest_dept_freq DESC);

CREATE INDEX idx_clusterization_freq_rota ON ml_clusterization (route_departure_freq DESC);

-- Índice para análise de valor por ticket
CREATE INDEX idx_clusterization_valor_ticket ON ml_clusterization (gmv_success, total_tickets_quantity_success);

-- Índice composto para análise completa de comportamento
CREATE INDEX idx_clusterization_comportamento ON ml_clusterization (cluster, is_weekend, period_of_day, gmv_success DESC);

-- Índice para consultas por versão do modelo
CREATE INDEX idx_clusterization_versao ON ml_clusterization (versao_modelo);

-- Índice para análise temporal por cluster
CREATE INDEX idx_clusterization_cluster_temporal ON ml_clusterization (cluster, date_purchase, is_weekend);

-- =====================================================
-- ÍNDICES ADICIONAIS PARA ml_recommendation
-- =====================================================

-- Índices para análise de probabilidades
CREATE INDEX idx_recommendation_prob1 ON ml_recommendation (prob_route_1 DESC);

CREATE INDEX idx_recommendation_prob_top3 ON ml_recommendation (prob_route_1 DESC, prob_route_2 DESC, prob_route_3 DESC);

-- Índices para outras rotas preditas
CREATE INDEX idx_recommendation_route2 ON ml_recommendation (predicted_route_2(100));

CREATE INDEX idx_recommendation_route3 ON ml_recommendation (predicted_route_3(100));

-- Índice composto para análise de recomendações por cliente
CREATE INDEX idx_recommendation_cliente_data ON ml_recommendation (fk_contact, date_purchase DESC);

-- Índice para análise de localização (nk_ota_localizer_id)
CREATE INDEX idx_recommendation_localizer ON ml_recommendation (nk_ota_localizer_id);

-- Índice composto para análise de contexto e recomendação
CREATE INDEX idx_recommendation_contexto ON ml_recommendation (route_departure(100), predicted_route_1(100));

-- Índice para análise temporal de recomendações
CREATE INDEX idx_recommendation_created_at ON ml_recommendation (created_at);

-- Índice composto para análise de performance das recomendações
CREATE INDEX idx_recommendation_performance ON ml_recommendation (prob_route_1 DESC, prob_route_2 DESC);

-- =====================================================
-- ÍNDICES PARA CONSULTAS CROSS-TABLE
-- =====================================================

-- Como as três tabelas compartilham fk_contact, vamos otimizar JOINs

-- Índice adicional em ml_classification para JOINs otimizados
CREATE INDEX idx_classification_contact_potencial ON ml_classification (fk_contact, potencial_recompra);

-- Índice adicional em ml_clusterization para JOINs otimizados  
CREATE INDEX idx_clusterization_contact_cluster ON ml_clusterization (fk_contact, cluster);

-- Índice adicional em ml_recommendation para JOINs otimizados
CREATE INDEX idx_recommendation_contact_prob ON ml_recommendation (fk_contact, prob_route_1 DESC);

-- =====================================================
-- ÍNDICES PARA ANÁLISES DE NEGÓCIO ESPECÍFICAS
-- =====================================================

-- Para identificar clientes de alto valor com baixo potencial (oportunidade de reativação)
CREATE INDEX idx_classification_reativacao ON ml_classification (gmv_total DESC, potencial_recompra, probabilidade_compra);

-- Para análise de sazonalidade por cluster
CREATE INDEX idx_clusterization_sazonalidade ON ml_clusterization (cluster, month, quarter);

-- Para análise de rotas mais recomendadas
CREATE INDEX idx_recommendation_top_routes ON ml_recommendation (predicted_route_1(100), prob_route_1 DESC);

-- Para análise de comportamento temporal de compras
CREATE INDEX idx_clusterization_time_analysis ON ml_clusterization (hour, period_of_day, day_of_week);

-- =====================================================
-- ÍNDICES PARA OTIMIZAÇÃO DE RELATÓRIOS
-- =====================================================

-- Para relatórios de performance do modelo de classificação
CREATE INDEX idx_classification_model_performance ON ml_classification (versao_modelo, data_predicao, target);

-- Para relatórios de distribuição de clusters
CREATE INDEX idx_clusterization_distribution ON ml_clusterization (cluster, versao_modelo, data_clusterizacao);

-- Para relatórios de eficácia das recomendações
CREATE INDEX idx_recommendation_effectiveness ON ml_recommendation (predicted_route_1(100), prob_route_1 DESC, created_at);

-- =====================================================
-- ESTATÍSTICAS DAS TABELAS PARA OTIMIZAÇÃO
-- =====================================================

-- Forçar atualização das estatísticas para o otimizador usar os novos índices
ANALYZE TABLE ml_classification;
ANALYZE TABLE ml_clusterization;  
ANALYZE TABLE ml_recommendation;

-- =====================================================
-- COMENTÁRIOS SOBRE OS ÍNDICES CRIADOS
-- =====================================================

/*
ÍNDICES DE PERFORMANCE CRÍTICA:

1. CLASSIFICAÇÃO:
   - idx_classification_potencial_prob: Otimiza consultas por categoria de risco ordenadas por probabilidade
   - idx_classification_rfm: Análise RFM (Recency, Frequency, Monetary) completa
   - idx_classification_campanha: Segmentação para campanhas de marketing

2. CLUSTERIZAÇÃO:
   - idx_clusterization_cluster_gmv: Análise financeira por cluster
   - idx_clusterization_comportamento: Análise comportamental completa
   - idx_clusterization_origem_destino: Otimiza consultas de rotas

3. RECOMENDAÇÃO:
   - idx_recommendation_prob_top3: Otimiza consultas das melhores recomendações
   - idx_recommendation_contexto: Análise de contexto vs recomendação
   - idx_recommendation_performance: Análise de eficácia das predições

CONSULTAS OTIMIZADAS:

- Segmentação de clientes por potencial e valor
- Análise temporal e sazonal de comportamento
- Identificação de padrões de rota por cluster
- Avaliação de performance dos modelos ML
- Relatórios de negócio para campanhas de marketing
- Análise de ROI por categoria de cliente

MANUTENÇÃO:

- Execute ANALYZE TABLE periodicamente para manter estatísticas atualizadas
- Monitore o uso dos índices com EXPLAIN PLAN
- Considere remover índices não utilizados após análise de performance
- Avalie a criação de índices parciais para dados específicos se necessário

TAMANHO ESTIMADO DOS ÍNDICES:

- ml_classification (572K registros): ~50-80MB de índices adicionais
- ml_clusterization (1.7M registros): ~200-300MB de índices adicionais  
- ml_recommendation (46K registros): ~5-10MB de índices adicionais

Total estimado: ~255-390MB de espaço adicional em disco
*/

-- =====================================================
-- VERIFICAÇÃO DOS ÍNDICES CRIADOS
-- =====================================================

-- Para verificar se os índices foram criados corretamente, execute:

-- SELECT 
--     TABLE_NAME,
--     INDEX_NAME,
--     COLUMN_NAME,
--     SEQ_IN_INDEX,
--     INDEX_TYPE
-- FROM INFORMATION_SCHEMA.STATISTICS 
-- WHERE TABLE_SCHEMA = 'enterprise_challenge' 
--   AND TABLE_NAME IN ('ml_classification', 'ml_clusterization', 'ml_recommendation')
-- ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX;

-- Para verificar o tamanho das tabelas e índices:

-- SELECT 
--     TABLE_NAME,
--     ROUND(((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024), 2) AS 'Total Size (MB)',
--     ROUND((DATA_LENGTH / 1024 / 1024), 2) AS 'Data Size (MB)',
--     ROUND((INDEX_LENGTH / 1024 / 1024), 2) AS 'Index Size (MB)'
-- FROM INFORMATION_SCHEMA.TABLES 
-- WHERE TABLE_SCHEMA = 'enterprise_challenge'
--   AND TABLE_NAME IN ('ml_classification', 'ml_clusterization', 'ml_recommendation');
