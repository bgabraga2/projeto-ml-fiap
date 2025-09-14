#!/usr/bin/env python3
"""
Script para verificar a integridade dos dados carregados no MySQL
Compara estatísticas dos CSVs originais com os dados no banco
"""

import pandas as pd
import mysql.connector
from mysql.connector import Error
import os
import sys
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def connect_to_db():
    """Conecta ao banco de dados MySQL"""
    try:
        config = {
            'host': 'mysql.orango.dev',
            'port': 3306,
            'user': 'root',
            'password': 'chp261190',
            'database': 'enterprise_challenge',
            'charset': 'utf8mb4'
        }
        
        connection = mysql.connector.connect(**config)
        return connection
    except Error as e:
        logger.error(f"Erro ao conectar ao MySQL: {e}")
        return None

def verify_classification_data():
    """Verifica integridade dos dados de classificação"""
    logger.info("=== Verificando dados de classificação ===")
    
    # Ler CSV original
    csv_path = '../dist/classification/dataset_recompra_completo.csv'
    if not os.path.exists(csv_path):
        logger.error(f"Arquivo CSV não encontrado: {csv_path}")
        return False
    
    df_csv = pd.read_csv(csv_path)
    logger.info(f"CSV - Total de registros: {len(df_csv):,}")
    
    # Conectar ao banco
    conn = connect_to_db()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # Verificar contagem total
        cursor.execute("SELECT COUNT(*) FROM ml_classification")
        db_count = cursor.fetchone()[0]
        logger.info(f"MySQL - Total de registros: {db_count:,}")
        
        if len(df_csv) != db_count:
            logger.warning(f"Diferença na contagem: CSV={len(df_csv)}, MySQL={db_count}")
        
        # Verificar distribuição de potencial de recompra
        csv_dist = df_csv['potencial_recompra'].value_counts().sort_index()
        logger.info("CSV - Distribuição por potencial:")
        for categoria, count in csv_dist.items():
            logger.info(f"  {categoria}: {count:,}")
        
        cursor.execute("""
            SELECT potencial_recompra, COUNT(*) as total
            FROM ml_classification 
            GROUP BY potencial_recompra
            ORDER BY potencial_recompra
        """)
        
        logger.info("MySQL - Distribuição por potencial:")
        for categoria, count in cursor.fetchall():
            logger.info(f"  {categoria}: {count:,}")
        
        # Verificar valores nulos
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN fk_contact IS NULL THEN 1 ELSE 0 END) as null_contact,
                SUM(CASE WHEN probabilidade_compra IS NULL THEN 1 ELSE 0 END) as null_prob,
                SUM(CASE WHEN target IS NULL THEN 1 ELSE 0 END) as null_target
            FROM ml_classification
        """)
        
        null_contact, null_prob, null_target = cursor.fetchone()
        logger.info(f"MySQL - Valores nulos: contact={null_contact}, prob={null_prob}, target={null_target}")
        
        return True
        
    except Error as e:
        logger.error(f"Erro ao verificar dados de classificação: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def verify_clusterization_data():
    """Verifica integridade dos dados de clusterização"""
    logger.info("=== Verificando dados de clusterização ===")
    
    # Conectar ao banco
    conn = connect_to_db()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # Verificar contagem total
        cursor.execute("SELECT COUNT(*) FROM ml_clusterization")
        db_count = cursor.fetchone()[0]
        logger.info(f"MySQL - Total de registros: {db_count:,}")
        
        # Verificar distribuição de clusters
        cursor.execute("""
            SELECT cluster, COUNT(*) as total
            FROM ml_clusterization 
            GROUP BY cluster
            ORDER BY cluster
        """)
        
        logger.info("MySQL - Distribuição por cluster:")
        for cluster, count in cursor.fetchall():
            logger.info(f"  Cluster {cluster}: {count:,}")
        
        # Verificar clientes únicos
        cursor.execute("SELECT COUNT(DISTINCT fk_contact) FROM ml_clusterization")
        unique_customers = cursor.fetchone()[0]
        logger.info(f"MySQL - Clientes únicos: {unique_customers:,}")
        
        # Verificar range de datas
        cursor.execute("""
            SELECT MIN(date_purchase) as min_date, MAX(date_purchase) as max_date
            FROM ml_clusterization
        """)
        min_date, max_date = cursor.fetchone()
        logger.info(f"MySQL - Range de datas: {min_date} a {max_date}")
        
        return True
        
    except Error as e:
        logger.error(f"Erro ao verificar dados de clusterização: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def verify_recommendation_data():
    """Verifica integridade dos dados de recomendação"""
    logger.info("=== Verificando dados de recomendação ===")
    
    # Ler CSV original
    csv_path = '../dist/recommendation/dataset_recomendacoes_completo.csv'
    if not os.path.exists(csv_path):
        logger.error(f"Arquivo CSV não encontrado: {csv_path}")
        return False
    
    df_csv = pd.read_csv(csv_path)
    logger.info(f"CSV - Total de registros: {len(df_csv):,}")
    logger.info(f"CSV - Colunas: {list(df_csv.columns)}")
    
    # Verificar colunas esperadas no CSV
    expected_csv_columns = [
        'nk_ota_localizer_id', 'fk_contact', 'date_purchase', 'route_departure',
        'predicted_route_1', 'predicted_route_2', 'predicted_route_3', 
        'predicted_route_4', 'predicted_route_5',
        'prob_route_1', 'prob_route_2', 'prob_route_3', 'prob_route_4', 'prob_route_5'
    ]
    
    missing_columns = [col for col in expected_csv_columns if col not in df_csv.columns]
    if missing_columns:
        logger.warning(f"CSV - Colunas ausentes: {missing_columns}")
    
    extra_columns = [col for col in df_csv.columns if col not in expected_csv_columns]
    if extra_columns:
        logger.info(f"CSV - Colunas extras: {extra_columns}")
    
    # Conectar ao banco
    conn = connect_to_db()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # Verificar estrutura da tabela MySQL
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'enterprise_challenge' 
            AND TABLE_NAME = 'ml_recommendation'
            ORDER BY ORDINAL_POSITION
        """)
        
        mysql_columns = cursor.fetchall()
        logger.info("MySQL - Estrutura da tabela:")
        mysql_column_names = []
        for col_name, data_type, is_nullable, default_val in mysql_columns:
            mysql_column_names.append(col_name)
            logger.info(f"  {col_name}: {data_type} {'NULL' if is_nullable == 'YES' else 'NOT NULL'}")
        
        # Verificar compatibilidade CSV vs MySQL
        csv_columns_set = set(df_csv.columns)
        mysql_data_columns = set([col for col in mysql_column_names if col not in ['id', 'created_at']])
        
        missing_in_mysql = csv_columns_set - mysql_data_columns
        missing_in_csv = mysql_data_columns - csv_columns_set
        
        if missing_in_mysql:
            logger.warning(f"Colunas no CSV mas não no MySQL: {missing_in_mysql}")
        if missing_in_csv:
            logger.warning(f"Colunas no MySQL mas não no CSV: {missing_in_csv}")
        if not missing_in_mysql and not missing_in_csv:
            logger.info("✅ Estrutura CSV e MySQL compatíveis")
        
        # Verificar contagem total
        cursor.execute("SELECT COUNT(*) FROM ml_recommendation")
        db_count = cursor.fetchone()[0]
        logger.info(f"MySQL - Total de registros: {db_count:,}")
        
        if len(df_csv) != db_count:
            logger.warning(f"Diferença na contagem: CSV={len(df_csv)}, MySQL={db_count}")
        
        # Verificar clientes únicos
        cursor.execute("SELECT COUNT(DISTINCT fk_contact) FROM ml_recommendation")
        unique_customers = cursor.fetchone()[0]
        logger.info(f"MySQL - Clientes únicos: {unique_customers:,}")
        
        # Verificar rotas únicas
        cursor.execute("SELECT COUNT(DISTINCT route_departure) FROM ml_recommendation WHERE route_departure IS NOT NULL")
        unique_routes = cursor.fetchone()[0]
        logger.info(f"MySQL - Rotas únicas: {unique_routes:,}")
        
        # Verificar top rotas preditas
        cursor.execute("""
            SELECT predicted_route_1, COUNT(*) as freq
            FROM ml_recommendation
            WHERE predicted_route_1 IS NOT NULL
            GROUP BY predicted_route_1
            ORDER BY freq DESC
            LIMIT 5
        """)
        
        logger.info("MySQL - Top 5 rotas mais preditas:")
        for route, freq in cursor.fetchall():
            route_short = route[:50] + "..." if len(route) > 50 else route
            logger.info(f"  {route_short}: {freq:,}")
        
        # Verificar probabilidades
        cursor.execute("""
            SELECT 
                AVG(prob_route_1) as avg_prob1,
                MIN(prob_route_1) as min_prob1,
                MAX(prob_route_1) as max_prob1,
                COUNT(CASE WHEN prob_route_1 IS NOT NULL THEN 1 END) as valid_probs
            FROM ml_recommendation
        """)
        
        avg_prob, min_prob, max_prob, valid_probs = cursor.fetchone()
        logger.info(f"MySQL - Probabilidades rota 1: avg={avg_prob:.4f}, min={min_prob:.4f}, max={max_prob:.4f}")
        logger.info(f"MySQL - Registros com probabilidade válida: {valid_probs:,}")
        
        # Verificar campos obrigatórios não nulos
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN fk_contact IS NULL THEN 1 ELSE 0 END) as null_contact,
                SUM(CASE WHEN predicted_route_1 IS NULL THEN 1 ELSE 0 END) as null_pred1,
                SUM(CASE WHEN prob_route_1 IS NULL THEN 1 ELSE 0 END) as null_prob1
            FROM ml_recommendation
        """)
        
        null_contact, null_pred1, null_prob1 = cursor.fetchone()
        logger.info(f"MySQL - Valores nulos: contact={null_contact}, pred1={null_pred1}, prob1={null_prob1}")
        
        # Verificar range de datas
        cursor.execute("""
            SELECT MIN(date_purchase) as min_date, MAX(date_purchase) as max_date
            FROM ml_recommendation
            WHERE date_purchase IS NOT NULL
        """)
        
        result = cursor.fetchone()
        if result and result[0]:
            min_date, max_date = result
            logger.info(f"MySQL - Range de datas: {min_date} a {max_date}")
        else:
            logger.info("MySQL - Nenhuma data válida encontrada")
        
        return True
        
    except Error as e:
        logger.error(f"Erro ao verificar dados de recomendação: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def generate_summary_report():
    """Gera um relatório resumo das tabelas"""
    logger.info("=== Relatório Resumo ===")
    
    conn = connect_to_db()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # Estatísticas gerais
        tables = ['ml_classification', 'ml_clusterization', 'ml_recommendation']
        
        logger.info("Estatísticas das tabelas:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            
            cursor.execute(f"""
                SELECT table_name, 
                       ROUND(((data_length + index_length) / 1024 / 1024), 2) as size_mb
                FROM information_schema.tables 
                WHERE table_schema = 'enterprise_challenge' 
                AND table_name = '{table}'
            """)
            
            result = cursor.fetchone()
            size_mb = result[1] if result else 0
            
            logger.info(f"  {table}: {count:,} registros, {size_mb} MB")
        
        # Verificar integridade referencial (clientes comuns)
        cursor.execute("""
            SELECT 
                (SELECT COUNT(DISTINCT fk_contact) FROM ml_classification) as classification_customers,
                (SELECT COUNT(DISTINCT fk_contact) FROM ml_clusterization) as clusterization_customers,
                (SELECT COUNT(DISTINCT fk_contact) FROM ml_recommendation) as recommendation_customers
        """)
        
        class_customers, cluster_customers, rec_customers = cursor.fetchone()
        logger.info(f"Clientes únicos por modelo:")
        logger.info(f"  Classificação: {class_customers:,}")
        logger.info(f"  Clusterização: {cluster_customers:,}")
        logger.info(f"  Recomendação: {rec_customers:,}")
        
        # Clientes em comum entre modelos
        cursor.execute("""
            SELECT COUNT(DISTINCT c.fk_contact)
            FROM ml_classification c
            INNER JOIN ml_clusterization cl ON c.fk_contact = cl.fk_contact
        """)
        common_class_cluster = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(DISTINCT c.fk_contact)
            FROM ml_classification c
            INNER JOIN ml_recommendation r ON c.fk_contact = r.fk_contact
        """)
        common_class_rec = cursor.fetchone()[0]
        
        logger.info(f"Clientes em comum:")
        logger.info(f"  Classificação ∩ Clusterização: {common_class_cluster:,}")
        logger.info(f"  Classificação ∩ Recomendação: {common_class_rec:,}")
        
        return True
        
    except Error as e:
        logger.error(f"Erro ao gerar relatório resumo: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def main():
    """Função principal"""
    logger.info("=== Verificação de Integridade dos Dados ML ===")
    
    success = True
    
    # Verificar cada modelo
    success &= verify_classification_data()
    success &= verify_clusterization_data() 
    success &= verify_recommendation_data()
    success &= generate_summary_report()
    
    if success:
        logger.info("=== Verificação concluída com sucesso ===")
    else:
        logger.error("=== Verificação concluída com erros ===")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
