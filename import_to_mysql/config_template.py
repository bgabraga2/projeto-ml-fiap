"""
Template de configuração para o carregamento de dados ML no MySQL
Copie este arquivo para config.py e ajuste as configurações conforme seu ambiente
"""

# Configurações do banco de dados MySQL
DB_CONFIG = {
    'host': 'mysql.orango.dev',
    'port': 3306,
    'user': 'root',
    'password': 'chp261190',  # ADICIONE SUA SENHA AQUI
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci',
    'autocommit': False
}

# Nome do banco de dados que será criado
DATABASE_NAME = 'enterprise_challenge'

# Configurações de carregamento
BATCH_SIZES = {
    'classification': 5000,
    'clusterization': 2000,  # Arquivo maior, batch menor
    'recommendation': 3000
}

# Caminhos dos arquivos CSV (relativos ao diretório do script)
CSV_PATHS = {
    'classification': '../dist/classification/dataset_recompra_completo.csv',
    'clusterization': '../dist/clusterization/dataset_com_clusters.csv',
    'recommendation': '../dist/recommendation/dataset_recomendacoes_completo.csv'
}
