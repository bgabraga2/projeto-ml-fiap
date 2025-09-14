-- =====================================================
-- Script de Verificação de Índices
-- Projeto ML FIAP - Verificação de Performance do Banco
-- =====================================================

-- Este script verifica se os índices foram criados corretamente
-- e fornece métricas de uso e performance

-- =====================================================
-- 1. VERIFICAR ÍNDICES EXISTENTES
-- =====================================================

SELECT 
    'ÍNDICES EXISTENTES POR TABELA' as info;

SELECT 
    TABLE_NAME as 'Tabela',
    INDEX_NAME as 'Nome do Índice',
    GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX) as 'Colunas',
    INDEX_TYPE as 'Tipo',
    NON_UNIQUE as 'Não Único',
    CARDINALITY as 'Cardinalidade'
FROM INFORMATION_SCHEMA.STATISTICS 
WHERE TABLE_SCHEMA = 'enterprise_challenge' 
  AND TABLE_NAME IN ('ml_classification', 'ml_clusterization', 'ml_recommendation')
GROUP BY TABLE_NAME, INDEX_NAME
ORDER BY TABLE_NAME, INDEX_NAME;

-- =====================================================
-- 2. VERIFICAR TAMANHO DAS TABELAS E ÍNDICES
-- =====================================================

SELECT 
    'TAMANHO DAS TABELAS E ÍNDICES' as info;

SELECT 
    TABLE_NAME as 'Tabela',
    TABLE_ROWS as 'Linhas (Estimado)',
    ROUND((DATA_LENGTH / 1024 / 1024), 2) AS 'Dados (MB)',
    ROUND((INDEX_LENGTH / 1024 / 1024), 2) AS 'Índices (MB)',
    ROUND(((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024), 2) AS 'Total (MB)',
    ROUND((INDEX_LENGTH * 100.0 / (DATA_LENGTH + INDEX_LENGTH)), 1) AS '% Índices'
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'enterprise_challenge'
  AND TABLE_NAME IN ('ml_classification', 'ml_clusterization', 'ml_recommendation')
ORDER BY (DATA_LENGTH + INDEX_LENGTH) DESC;

-- =====================================================
-- 3. VERIFICAR FRAGMENTAÇÃO DOS ÍNDICES
-- =====================================================

SELECT 
    'FRAGMENTAÇÃO DAS TABELAS' as info;

SELECT 
    TABLE_NAME as 'Tabela',
    DATA_FREE as 'Espaço Livre (bytes)',
    ROUND((DATA_FREE / 1024 / 1024), 2) as 'Espaço Livre (MB)',
    CASE 
        WHEN DATA_FREE > 0 THEN 'Considere OPTIMIZE TABLE'
        ELSE 'OK'
    END as 'Recomendação'
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'enterprise_challenge'
  AND TABLE_NAME IN ('ml_classification', 'ml_clusterization', 'ml_recommendation');

-- =====================================================
-- 4. CONSULTAS DE EXEMPLO PARA TESTAR ÍNDICES
-- =====================================================

-- Teste 1: Consulta por potencial de recompra (deve usar idx_classification_potencial_prob)
EXPLAIN FORMAT=JSON
SELECT fk_contact, probabilidade_compra, gmv_total 
FROM ml_classification 
WHERE potencial_recompra = 'Alto' 
ORDER BY probabilidade_compra DESC 
LIMIT 100;

-- Teste 2: Consulta por cluster e GMV (deve usar idx_clusterization_cluster_gmv)
EXPLAIN FORMAT=JSON
SELECT cluster, AVG(gmv_success), COUNT(*) 
FROM ml_clusterization 
WHERE cluster = 1 
GROUP BY cluster;

-- Teste 3: Consulta por recomendações (deve usar idx_recommendation_prob1)
EXPLAIN FORMAT=JSON
SELECT fk_contact, predicted_route_1, prob_route_1 
FROM ml_recommendation 
WHERE prob_route_1 > 0.1 
ORDER BY prob_route_1 DESC 
LIMIT 50;

-- Teste 4: JOIN entre tabelas (deve usar índices de fk_contact)
EXPLAIN FORMAT=JSON
SELECT 
    c.fk_contact,
    c.potencial_recompra,
    cl.cluster,
    r.predicted_route_1
FROM ml_classification c
JOIN ml_clusterization cl ON c.fk_contact = cl.fk_contact
LEFT JOIN ml_recommendation r ON c.fk_contact = r.fk_contact
WHERE c.potencial_recompra IN ('Alto', 'Muito Alto')
LIMIT 100;

-- =====================================================
-- 5. ANÁLISE DE CARDINALIDADE DOS ÍNDICES
-- =====================================================

SELECT 
    'ANÁLISE DE CARDINALIDADE' as info;

-- Verificar distribuição de valores em colunas indexadas
SELECT 
    'ml_classification - potencial_recompra' as coluna,
    potencial_recompra as valor,
    COUNT(*) as frequencia,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM ml_classification), 2) as percentual
FROM ml_classification 
GROUP BY potencial_recompra 
ORDER BY frequencia DESC;

SELECT 
    'ml_clusterization - cluster' as coluna,
    cluster as valor,
    COUNT(*) as frequencia,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM ml_clusterization), 2) as percentual
FROM ml_clusterization 
GROUP BY cluster 
ORDER BY cluster;

SELECT 
    'ml_clusterization - is_weekend' as coluna,
    is_weekend as valor,
    COUNT(*) as frequencia,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM ml_clusterization), 2) as percentual
FROM ml_clusterization 
GROUP BY is_weekend;

-- =====================================================
-- 6. ÍNDICES DUPLICADOS OU REDUNDANTES
-- =====================================================

SELECT 
    'VERIFICAÇÃO DE ÍNDICES REDUNDANTES' as info;

-- Buscar índices que podem ser redundantes
SELECT 
    s1.TABLE_NAME,
    s1.INDEX_NAME as 'Índice 1',
    s2.INDEX_NAME as 'Índice 2',
    GROUP_CONCAT(s1.COLUMN_NAME ORDER BY s1.SEQ_IN_INDEX) as 'Colunas Índice 1',
    GROUP_CONCAT(s2.COLUMN_NAME ORDER BY s2.SEQ_IN_INDEX) as 'Colunas Índice 2'
FROM INFORMATION_SCHEMA.STATISTICS s1
JOIN INFORMATION_SCHEMA.STATISTICS s2 ON 
    s1.TABLE_SCHEMA = s2.TABLE_SCHEMA 
    AND s1.TABLE_NAME = s2.TABLE_NAME 
    AND s1.INDEX_NAME < s2.INDEX_NAME
WHERE s1.TABLE_SCHEMA = 'enterprise_challenge'
  AND s1.TABLE_NAME IN ('ml_classification', 'ml_clusterization', 'ml_recommendation')
GROUP BY s1.TABLE_NAME, s1.INDEX_NAME, s2.INDEX_NAME
HAVING GROUP_CONCAT(s1.COLUMN_NAME ORDER BY s1.SEQ_IN_INDEX) = 
       GROUP_CONCAT(s2.COLUMN_NAME ORDER BY s2.SEQ_IN_INDEX);

-- =====================================================
-- 7. RECOMENDAÇÕES DE OTIMIZAÇÃO
-- =====================================================

SELECT 
    'RECOMENDAÇÕES DE OTIMIZAÇÃO' as info;

-- Verificar tabelas que podem precisar de OPTIMIZE
SELECT 
    TABLE_NAME as 'Tabela',
    CASE 
        WHEN DATA_FREE > (DATA_LENGTH * 0.1) THEN 'Execute: OPTIMIZE TABLE ' + TABLE_NAME + ';'
        WHEN INDEX_LENGTH > (DATA_LENGTH * 2) THEN 'Muitos índices - revisar necessidade'
        WHEN TABLE_ROWS = 0 THEN 'Tabela vazia - execute ANALYZE TABLE'
        ELSE 'Tabela otimizada'
    END as 'Recomendação'
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'enterprise_challenge'
  AND TABLE_NAME IN ('ml_classification', 'ml_clusterization', 'ml_recommendation');

-- =====================================================
-- 8. COMANDOS DE MANUTENÇÃO
-- =====================================================

SELECT 
    'COMANDOS DE MANUTENÇÃO SUGERIDOS' as info;

SELECT 
    'Para atualizar estatísticas dos índices, execute:' as comando
UNION ALL
SELECT 'ANALYZE TABLE ml_classification;'
UNION ALL  
SELECT 'ANALYZE TABLE ml_clusterization;'
UNION ALL
SELECT 'ANALYZE TABLE ml_recommendation;'
UNION ALL
SELECT ''
UNION ALL
SELECT 'Para otimizar tabelas fragmentadas, execute:'
UNION ALL
SELECT 'OPTIMIZE TABLE ml_classification;'
UNION ALL
SELECT 'OPTIMIZE TABLE ml_clusterization;'
UNION ALL
SELECT 'OPTIMIZE TABLE ml_recommendation;'
UNION ALL
SELECT ''
UNION ALL
SELECT 'Para verificar uso de índices em consultas específicas:'
UNION ALL
SELECT 'Use EXPLAIN ou EXPLAIN FORMAT=JSON antes das consultas';

-- =====================================================
-- 9. MONITORAMENTO DE PERFORMANCE
-- =====================================================

-- Query para verificar se os índices estão sendo utilizados
-- (Requer MySQL 5.6+ com Performance Schema habilitado)

SELECT 
    'MONITORAMENTO DE USO DOS ÍNDICES' as info;

-- Verificar se o Performance Schema está habilitado
SELECT 
    VARIABLE_NAME,
    VARIABLE_VALUE
FROM INFORMATION_SCHEMA.GLOBAL_VARIABLES 
WHERE VARIABLE_NAME = 'performance_schema';

-- Se Performance Schema estiver habilitado, você pode usar:
-- SELECT 
--     OBJECT_SCHEMA,
--     OBJECT_NAME,
--     INDEX_NAME,
--     COUNT_FETCH,
--     COUNT_INSERT,
--     COUNT_UPDATE,
--     COUNT_DELETE
-- FROM performance_schema.table_io_waits_summary_by_index_usage
-- WHERE OBJECT_SCHEMA = 'enterprise_challenge'
--   AND OBJECT_NAME IN ('ml_classification', 'ml_clusterization', 'ml_recommendation')
-- ORDER BY COUNT_FETCH DESC;

-- =====================================================
-- 10. RESUMO FINAL
-- =====================================================

SELECT 
    'RESUMO DA VERIFICAÇÃO' as info;

SELECT 
    COUNT(DISTINCT TABLE_NAME) as 'Tabelas Verificadas',
    COUNT(DISTINCT INDEX_NAME) as 'Índices Encontrados',
    SUM(ROUND((INDEX_LENGTH / 1024 / 1024), 2)) as 'Tamanho Total Índices (MB)',
    AVG(CARDINALITY) as 'Cardinalidade Média'
FROM INFORMATION_SCHEMA.STATISTICS s
JOIN INFORMATION_SCHEMA.TABLES t ON s.TABLE_SCHEMA = t.TABLE_SCHEMA AND s.TABLE_NAME = t.TABLE_NAME
WHERE s.TABLE_SCHEMA = 'enterprise_challenge'
  AND s.TABLE_NAME IN ('ml_classification', 'ml_clusterization', 'ml_recommendation');

-- =====================================================
-- INSTRUÇÕES DE USO
-- =====================================================

/*
COMO USAR ESTE SCRIPT:

1. Execute este script completo no MySQL para verificar os índices
2. Analise os resultados das consultas EXPLAIN para confirmar uso dos índices
3. Execute os comandos de manutenção sugeridos se necessário
4. Monitore a performance das consultas mais frequentes

INTERPRETAÇÃO DOS RESULTADOS:

- Cardinalidade alta = índice mais seletivo (melhor)
- % Índices muito alto (>50%) pode indicar excesso de índices
- Fragmentação alta requer OPTIMIZE TABLE
- Consultas EXPLAIN devem mostrar uso de índices (key != NULL)

MANUTENÇÃO RECOMENDADA:

- Execute ANALYZE TABLE semanalmente
- Execute OPTIMIZE TABLE mensalmente ou quando fragmentação > 10%
- Monitore consultas lentas e adicione índices conforme necessário
- Remova índices não utilizados após análise de performance
*/
