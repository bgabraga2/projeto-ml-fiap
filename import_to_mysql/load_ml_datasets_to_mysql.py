#!/usr/bin/env python3
"""
Script para carregar os datasets dos modelos de ML no MySQL
Cria as tabelas e insere os dados dos CSVs exportados pelos modelos:
- Classification: dataset_recompra_completo.csv
- Clusterization: dataset_com_clusters.csv  
- Recommendation: dataset_recomendacoes_completo.csv
"""

import pandas as pd
import mysql.connector
from mysql.connector import Error
import os
import sys
from datetime import datetime
import logging
from typing import Optional, Dict, Any
import warnings
warnings.filterwarnings('ignore')

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ml_data_load.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MLDataLoader:
    """Classe para carregar dados dos modelos ML no MySQL"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o carregador de dados
        
        Args:
            config: Dicionário com configurações do banco de dados
        """
        self.config = config
        self.connection: Optional[mysql.connector.MySQLConnection] = None
        self.cursor: Optional[mysql.connector.cursor.MySQLCursor] = None
        
    def connect(self) -> bool:
        """
        Conecta ao banco de dados MySQL
        
        Returns:
            bool: True se conectou com sucesso, False caso contrário
        """
        try:
            self.connection = mysql.connector.connect(**self.config)
            self.cursor = self.connection.cursor()
            logger.info("Conectado ao MySQL com sucesso")
            return True
        except Error as e:
            logger.error(f"Erro ao conectar ao MySQL: {e}")
            return False
    
    def disconnect(self):
        """Desconecta do banco de dados"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("Desconectado do MySQL")
    
    def create_database(self, database_name: str) -> bool:
        """
        Cria o banco de dados se não existir
        
        Args:
            database_name: Nome do banco de dados
            
        Returns:
            bool: True se criou ou já existe, False caso contrário
        """
        try:
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
            self.cursor.execute(f"USE {database_name}")
            self.connection.commit()
            logger.info(f"Banco de dados '{database_name}' criado/selecionado")
            return True
        except Error as e:
            logger.error(f"Erro ao criar/selecionar banco de dados: {e}")
            return False
    
    def create_classification_table(self) -> bool:
        """
        Cria a tabela para o modelo de classificação
        
        Returns:
            bool: True se criou com sucesso, False caso contrário
        """
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS ml_classification (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            fk_contact VARCHAR(255) NOT NULL,
            data_ultima_compra DATE,
            target TINYINT(1),
            probabilidade_compra DECIMAL(10,6),
            predicao_compra TINYINT(1),
            potencial_recompra ENUM('Baixo', 'Médio', 'Alto', 'Muito Alto'),
            gmv_ultima_compra DECIMAL(10,2),
            tickets_ultima_compra INT,
            dias_desde_ultima_compra INT,
            total_compras INT,
            gmv_total DECIMAL(12,2),
            gmv_medio DECIMAL(10,2),
            mes_ultima_compra TINYINT,
            ano_ultima_compra YEAR,
            origens_unicas INT,
            destinos_unicos INT,
            empresas_unicas INT,
            intervalo_medio_dias DECIMAL(10,2),
            regularidade DECIMAL(10,2),
            data_predicao DATETIME,
            versao_modelo VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_fk_contact (fk_contact),
            INDEX idx_potencial (potencial_recompra),
            INDEX idx_probabilidade (probabilidade_compra),
            INDEX idx_target (target)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        try:
            self.cursor.execute("DROP TABLE IF EXISTS ml_classification")
            self.cursor.execute(create_table_sql)
            self.connection.commit()
            logger.info("Tabela ml_classification criada com sucesso")
            return True
        except Error as e:
            logger.error(f"Erro ao criar tabela ml_classification: {e}")
            return False
    
    def create_clusterization_table(self) -> bool:
        """
        Cria a tabela para o modelo de clusterização
        
        Returns:
            bool: True se criou com sucesso, False caso contrário
        """
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS ml_clusterization (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            nk_ota_localizer_id VARCHAR(255),
            fk_contact VARCHAR(255) NOT NULL,
            date_purchase DATE,
            time_purchase TIME,
            place_origin_departure VARCHAR(255),
            place_destination_departure VARCHAR(255),
            place_origin_return VARCHAR(255),
            place_destination_return VARCHAR(255),
            fk_departure_ota_bus_company VARCHAR(255),
            fk_return_ota_bus_company VARCHAR(255),
            gmv_success DECIMAL(10,2),
            total_tickets_quantity_success INT,
            day_of_week TINYINT,
            month TINYINT,
            quarter TINYINT,
            is_weekend TINYINT(1),
            hour TINYINT,
            period_of_day VARCHAR(20),
            route_departure TEXT,
            route_return TEXT,
            is_round_trip TINYINT(1),
            departure_company_freq INT,
            return_company_freq INT,
            origin_dept_freq INT,
            dest_dept_freq INT,
            route_departure_freq INT,
            cluster TINYINT,
            data_clusterizacao DATETIME,
            versao_modelo VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_fk_contact (fk_contact),
            INDEX idx_cluster (cluster),
            INDEX idx_date_purchase (date_purchase),
            INDEX idx_route_departure (route_departure(100))
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        try:
            self.cursor.execute("DROP TABLE IF EXISTS ml_clusterization")
            self.cursor.execute(create_table_sql)
            self.connection.commit()
            logger.info("Tabela ml_clusterization criada com sucesso")
            return True
        except Error as e:
            logger.error(f"Erro ao criar tabela ml_clusterization: {e}")
            return False
    
    def create_recommendation_table(self) -> bool:
        """
        Cria a tabela para o modelo de recomendação (schema simplificado)
        
        Returns:
            bool: True se criou com sucesso, False caso contrário
        """
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS ml_recommendation (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            nk_ota_localizer_id VARCHAR(255),
            fk_contact VARCHAR(255) NOT NULL,
            date_purchase DATE,
            route_departure TEXT,
            predicted_route_1 TEXT,
            predicted_route_2 TEXT,
            predicted_route_3 TEXT,
            predicted_route_4 TEXT,
            predicted_route_5 TEXT,
            prob_route_1 DECIMAL(10,6),
            prob_route_2 DECIMAL(10,6),
            prob_route_3 DECIMAL(10,6),
            prob_route_4 DECIMAL(10,6),
            prob_route_5 DECIMAL(10,6),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_fk_contact (fk_contact),
            INDEX idx_date_purchase (date_purchase),
            INDEX idx_route_departure (route_departure(100)),
            INDEX idx_predicted_route_1 (predicted_route_1(100))
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        try:
            self.cursor.execute("DROP TABLE IF EXISTS ml_recommendation")
            self.cursor.execute(create_table_sql)
            self.connection.commit()
            logger.info("Tabela ml_recommendation criada com sucesso")
            return True
        except Error as e:
            logger.error(f"Erro ao criar tabela ml_recommendation: {e}")
            return False
    
    def load_classification_data(self, csv_path: str, batch_size: int = 1000) -> bool:
        """
        Carrega dados do modelo de classificação
        
        Args:
            csv_path: Caminho para o arquivo CSV
            batch_size: Tamanho do lote para inserção
            
        Returns:
            bool: True se carregou com sucesso, False caso contrário
        """
        try:
            if not os.path.exists(csv_path):
                logger.error(f"Arquivo não encontrado: {csv_path}")
                return False
                
            logger.info(f"Carregando dados de classificação de: {csv_path}")
            
            # Ler CSV em chunks para otimizar memória
            chunk_count = 0
            total_rows = 0
            
            for chunk in pd.read_csv(csv_path, chunksize=batch_size):
                chunk_count += 1
                
                # Preparar dados para inserção
                chunk = chunk.where(pd.notnull(chunk), None)
                
                # Converter datetime strings para formato MySQL
                if 'data_ultima_compra' in chunk.columns:
                    chunk['data_ultima_compra'] = pd.to_datetime(chunk['data_ultima_compra']).dt.date
                if 'data_predicao' in chunk.columns:
                    chunk['data_predicao'] = pd.to_datetime(chunk['data_predicao'])
                
                # SQL de inserção
                insert_sql = """
                INSERT INTO ml_classification (
                    fk_contact, data_ultima_compra, target, probabilidade_compra,
                    predicao_compra, potencial_recompra, gmv_ultima_compra, tickets_ultima_compra,
                    dias_desde_ultima_compra, total_compras, gmv_total, gmv_medio,
                    mes_ultima_compra, ano_ultima_compra, origens_unicas, destinos_unicos,
                    empresas_unicas, intervalo_medio_dias, regularidade, data_predicao, versao_modelo
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                # Preparar dados para inserção
                data_to_insert = []
                for _, row in chunk.iterrows():
                    data_to_insert.append(tuple(row[col] for col in [
                        'fk_contact', 'data_ultima_compra', 'target', 'probabilidade_compra',
                        'predicao_compra', 'potencial_recompra', 'gmv_ultima_compra', 'tickets_ultima_compra',
                        'dias_desde_ultima_compra', 'total_compras', 'gmv_total', 'gmv_medio',
                        'mes_ultima_compra', 'ano_ultima_compra', 'origens_unicas', 'destinos_unicos',
                        'empresas_unicas', 'intervalo_medio_dias', 'regularidade', 'data_predicao', 'versao_modelo'
                    ]))
                
                # Executar inserção em lote
                self.cursor.executemany(insert_sql, data_to_insert)
                self.connection.commit()
                
                total_rows += len(data_to_insert)
                logger.info(f"Chunk {chunk_count}: {len(data_to_insert)} registros inseridos")
            
            logger.info(f"Dados de classificação carregados: {total_rows:,} registros")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao carregar dados de classificação: {e}")
            self.connection.rollback()
            return False
    
    def load_clusterization_data(self, csv_path: str, batch_size: int = 1000) -> bool:
        """
        Carrega dados do modelo de clusterização
        
        Args:
            csv_path: Caminho para o arquivo CSV
            batch_size: Tamanho do lote para inserção
            
        Returns:
            bool: True se carregou com sucesso, False caso contrário
        """
        try:
            if not os.path.exists(csv_path):
                logger.error(f"Arquivo não encontrado: {csv_path}")
                return False
                
            logger.info(f"Carregando dados de clusterização de: {csv_path}")
            
            chunk_count = 0
            total_rows = 0
            
            for chunk in pd.read_csv(csv_path, chunksize=batch_size):
                chunk_count += 1
                
                # Preparar dados para inserção
                chunk = chunk.where(pd.notnull(chunk), None)
                
                # Converter datetime strings para formato MySQL
                if 'date_purchase' in chunk.columns:
                    chunk['date_purchase'] = pd.to_datetime(chunk['date_purchase']).dt.date
                if 'time_purchase' in chunk.columns:
                    # Extrair apenas o tempo da string datetime
                    chunk['time_purchase'] = pd.to_datetime(chunk['time_purchase']).dt.time
                if 'data_clusterizacao' in chunk.columns:
                    chunk['data_clusterizacao'] = pd.to_datetime(chunk['data_clusterizacao'])
                
                # SQL de inserção
                insert_sql = """
                INSERT INTO ml_clusterization (
                    nk_ota_localizer_id, fk_contact, date_purchase, time_purchase,
                    place_origin_departure, place_destination_departure, place_origin_return,
                    place_destination_return, fk_departure_ota_bus_company, fk_return_ota_bus_company,
                    gmv_success, total_tickets_quantity_success, day_of_week, month, quarter,
                    is_weekend, hour, period_of_day, route_departure, route_return, is_round_trip,
                    departure_company_freq, return_company_freq, origin_dept_freq, dest_dept_freq,
                    route_departure_freq, cluster, data_clusterizacao, versao_modelo
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                # Preparar dados para inserção
                data_to_insert = []
                for _, row in chunk.iterrows():
                    data_to_insert.append(tuple(row[col] for col in [
                        'nk_ota_localizer_id', 'fk_contact', 'date_purchase', 'time_purchase',
                        'place_origin_departure', 'place_destination_departure', 'place_origin_return',
                        'place_destination_return', 'fk_departure_ota_bus_company', 'fk_return_ota_bus_company',
                        'gmv_success', 'total_tickets_quantity_success', 'day_of_week', 'month', 'quarter',
                        'is_weekend', 'hour', 'period_of_day', 'route_departure', 'route_return', 'is_round_trip',
                        'departure_company_freq', 'return_company_freq', 'origin_dept_freq', 'dest_dept_freq',
                        'route_departure_freq', 'cluster', 'data_clusterizacao', 'versao_modelo'
                    ]))
                
                # Executar inserção em lote
                self.cursor.executemany(insert_sql, data_to_insert)
                self.connection.commit()
                
                total_rows += len(data_to_insert)
                logger.info(f"Chunk {chunk_count}: {len(data_to_insert)} registros inseridos")
            
            logger.info(f"Dados de clusterização carregados: {total_rows:,} registros")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao carregar dados de clusterização: {e}")
            self.connection.rollback()
            return False
    
    def load_recommendation_data(self, csv_path: str, batch_size: int = 1000) -> bool:
        """
        Carrega dados do modelo de recomendação (schema simplificado)
        
        Args:
            csv_path: Caminho para o arquivo CSV
            batch_size: Tamanho do lote para inserção
            
        Returns:
            bool: True se carregou com sucesso, False caso contrário
        """
        try:
            if not os.path.exists(csv_path):
                logger.error(f"Arquivo não encontrado: {csv_path}")
                return False
                
            logger.info(f"Carregando dados de recomendação de: {csv_path}")
            
            chunk_count = 0
            total_rows = 0
            
            for chunk in pd.read_csv(csv_path, chunksize=batch_size):
                chunk_count += 1
                
                # Preparar dados para inserção
                chunk = chunk.where(pd.notnull(chunk), None)
                
                # Converter datetime strings para formato MySQL
                if 'date_purchase' in chunk.columns:
                    chunk['date_purchase'] = pd.to_datetime(chunk['date_purchase'], errors='coerce').dt.date
                
                # SQL de inserção simplificado
                insert_sql = """
                INSERT INTO ml_recommendation (
                    nk_ota_localizer_id, fk_contact, date_purchase, route_departure,
                    predicted_route_1, predicted_route_2, predicted_route_3,
                    predicted_route_4, predicted_route_5, prob_route_1, prob_route_2, 
                    prob_route_3, prob_route_4, prob_route_5
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                # Preparar dados para inserção
                data_to_insert = []
                for _, row in chunk.iterrows():
                    data_to_insert.append(tuple(row[col] for col in [
                        'nk_ota_localizer_id', 'fk_contact', 'date_purchase', 'route_departure',
                        'predicted_route_1', 'predicted_route_2', 'predicted_route_3',
                        'predicted_route_4', 'predicted_route_5', 'prob_route_1', 'prob_route_2', 
                        'prob_route_3', 'prob_route_4', 'prob_route_5'
                    ]))
                
                # Executar inserção em lote
                self.cursor.executemany(insert_sql, data_to_insert)
                self.connection.commit()
                
                total_rows += len(data_to_insert)
                logger.info(f"Chunk {chunk_count}: {len(data_to_insert)} registros inseridos")
            
            logger.info(f"Dados de recomendação carregados: {total_rows:,} registros")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao carregar dados de recomendação: {e}")
            self.connection.rollback()
            return False
    
    def get_table_stats(self) -> Dict[str, int]:
        """
        Obtém estatísticas das tabelas criadas
        
        Returns:
            Dict com contagem de registros por tabela
        """
        stats = {}
        tables = ['ml_classification', 'ml_clusterization', 'ml_recommendation']
        
        for table in tables:
            try:
                self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = self.cursor.fetchone()[0]
                stats[table] = count
            except Error as e:
                logger.error(f"Erro ao obter estatísticas da tabela {table}: {e}")
                stats[table] = -1
                
        return stats

def main():
    """Função principal"""
    logger.info("=== Iniciando carregamento de dados ML no MySQL ===")
    
    # Configurações do banco de dados
    # ATENÇÃO: Altere essas configurações conforme seu ambiente
    db_config = {
        'host': 'mysql.orango.dev',
        'port': 3306,
        'user': 'root',
        'password': 'chp261190',
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci',
        'autocommit': False
    }
    
    database_name = 'enterprise_challenge'
    
    # Caminhos dos arquivos CSV
    base_dir = os.path.join(os.path.dirname(__file__), '..', 'dist')
    csv_files = {
        'classification': os.path.join(base_dir, 'classification', 'dataset_recompra_completo.csv'),
        'clusterization': os.path.join(base_dir, 'clusterization', 'dataset_com_clusters.csv'),
        'recommendation': os.path.join(base_dir, 'recommendation', 'dataset_recomendacoes_completo.csv')
    }
    
    # Verificar se os arquivos existem
    for name, path in csv_files.items():
        if not os.path.exists(path):
            logger.error(f"Arquivo CSV não encontrado: {path}")
            return False
        else:
            file_size = os.path.getsize(path) / (1024 * 1024)  # MB
            logger.info(f"Arquivo {name}: {path} ({file_size:.1f} MB)")
    
    # Inicializar carregador
    loader = MLDataLoader(db_config)
    
    try:
        # Conectar ao banco
        if not loader.connect():
            logger.error("Falha na conexão com o banco de dados")
            return False
        
        # Criar banco de dados
        if not loader.create_database(database_name):
            logger.error("Falha ao criar/selecionar banco de dados")
            return False
        
        # Criar tabelas
        logger.info("Criando tabelas...")
        if not all([
            loader.create_classification_table(),
            loader.create_clusterization_table(),
            loader.create_recommendation_table()
        ]):
            logger.error("Falha ao criar uma ou mais tabelas")
            return False
        
        # Carregar dados
        logger.info("Carregando dados...")
        
        start_time = datetime.now()
        
        # Carregar dados de classificação
        if not loader.load_classification_data(csv_files['classification'], batch_size=5000):
            logger.error("Falha ao carregar dados de classificação")
            return False
        
        # Carregar dados de clusterização (arquivo grande, batch menor)
        if not loader.load_clusterization_data(csv_files['clusterization'], batch_size=2000):
            logger.error("Falha ao carregar dados de clusterização")
            return False
        
        # Carregar dados de recomendação
        if not loader.load_recommendation_data(csv_files['recommendation'], batch_size=3000):
            logger.error("Falha ao carregar dados de recomendação")
            return False
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Obter estatísticas finais
        stats = loader.get_table_stats()
        
        logger.info("=== CARREGAMENTO CONCLUÍDO ===")
        logger.info(f"Tempo total: {duration}")
        logger.info("Estatísticas das tabelas:")
        for table, count in stats.items():
            logger.info(f"  {table}: {count:,} registros")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro durante o carregamento: {e}")
        return False
    
    finally:
        loader.disconnect()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
