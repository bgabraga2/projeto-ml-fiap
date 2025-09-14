# Script de Carregamento de Dados ML no MySQL

Este script carrega os datasets dos modelos de Machine Learning (classificação, clusterização e recomendação) em um banco de dados MySQL.

## Funcionalidades

- **Criação automática do banco de dados** e tabelas
- **Carregamento em lotes** para otimizar performance e uso de memória
- **Tratamento de tipos de dados** específicos para MySQL
- **Logging detalhado** do processo
- **Estatísticas finais** de carregamento

## Pré-requisitos

### 1. MySQL Server

Certifique-se de ter o MySQL Server instalado e rodando:

```bash
# No macOS com Homebrew
brew install mysql
brew services start mysql

# No Ubuntu/Debian
sudo apt install mysql-server
sudo systemctl start mysql
```

### 2. Python Dependencies

Instale as dependências Python:

```bash
cd scripts
pip install -r requirements.txt
```

### 3. Configuração do Banco de Dados

Crie um usuário MySQL com privilégios adequados:

```sql
-- Conecte como root
mysql -u root -p

-- Crie um usuário (opcional)
CREATE USER 'ml_user'@'localhost' IDENTIFIED BY 'sua_senha_aqui';
GRANT ALL PRIVILEGES ON *.* TO 'ml_user'@'localhost';
FLUSH PRIVILEGES;
```

## Configuração

### 1. Configurar Credenciais

Edite o arquivo `load_ml_datasets_to_mysql.py` e ajuste as configurações do banco na seção `db_config`:

```python
db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'seu_usuario',  # Altere conforme necessário
    'password': 'sua_senha',  # Adicione sua senha aqui
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci',
    'autocommit': False
}
```

### 2. Verificar Arquivos CSV

Certifique-se de que os seguintes arquivos existem:

- `../dist/classification/dataset_recompra_completo.csv`
- `../dist/clusterization/dataset_com_clusters.csv`
- `../dist/recommendation/dataset_recomendacoes_completo.csv`

## Execução

Execute o script a partir do diretório `scripts`:

```bash
cd scripts
python load_ml_datasets_to_mysql.py
```

## Estrutura das Tabelas

### 1. ml_classification

Dados do modelo de classificação para predição de recompra:

- **Registros**: ~573k clientes
- **Campos principais**: `fk_contact`, `probabilidade_compra`, `potencial_recompra`, `target`
- **Índices**: Por cliente, potencial, probabilidade e target

### 2. ml_clusterization

Dados do modelo de clusterização de clientes:

- **Registros**: ~1.7M transações
- **Campos principais**: `fk_contact`, `cluster`, `route_departure`, dados de viagem
- **Índices**: Por cliente, cluster, data e rota

### 3. ml_recommendation

Dados do modelo de recomendação de rotas:

- **Registros**: ~46k sequências de viagem
- **Campos principais**: `fk_contact`, `predicted_route_1-5`, `prob_route_1-5`
- **Índices**: Por cliente, cluster, data e rota predita

## Logs e Monitoramento

O script gera logs detalhados:

- **Console**: Progresso em tempo real
- **Arquivo**: `ml_data_load.log` (no diretório scripts)

Exemplo de saída:

```
2024-01-15 10:30:00 - INFO - Conectado ao MySQL com sucesso
2024-01-15 10:30:01 - INFO - Banco de dados 'projeto_ml_fiap' criado/selecionado
2024-01-15 10:30:02 - INFO - Tabela ml_classification criada com sucesso
2024-01-15 10:30:15 - INFO - Chunk 1: 5000 registros inseridos
...
2024-01-15 10:45:30 - INFO - === CARREGAMENTO CONCLUÍDO ===
2024-01-15 10:45:30 - INFO - Estatísticas das tabelas:
2024-01-15 10:45:30 - INFO -   ml_classification: 572,993 registros
2024-01-15 10:45:30 - INFO -   ml_clusterization: 1,741,344 registros
2024-01-15 10:45:30 - INFO -   ml_recommendation: 45,769 registros
```

## Otimizações Implementadas

1. **Carregamento em lotes**: Processa dados em chunks para otimizar memória
2. **Batch sizes otimizados**: Diferentes tamanhos por dataset conforme volume
3. **Índices estratégicos**: Para consultas frequentes por cliente, cluster, etc.
4. **Tipos de dados otimizados**: DECIMAL para precisão, ENUM para categorias
5. **Encoding UTF-8**: Suporte completo a caracteres especiais

## Troubleshooting

### Erro de Conexão

```
mysql.connector.errors.ProgrammingError: 1045 (28000): Access denied
```

**Solução**: Verifique usuário/senha no `db_config`

### Arquivo CSV não encontrado

```
Arquivo não encontrado: ../dist/classification/dataset_recompra_completo.csv
```

**Solução**: Execute primeiro os notebooks de ML para gerar os CSVs

### Erro de Memória

```
MemoryError: Unable to allocate array
```

**Solução**: Reduza os `batch_size` no código (principalmente para clusterização)

### Tabela já existe

O script automaticamente remove e recria as tabelas. Para preservar dados existentes, comente as linhas `DROP TABLE IF EXISTS`.

## Consultas Úteis

Após o carregamento, algumas consultas úteis:

```sql
-- Verificar carregamento
SELECT COUNT(*) FROM ml_classification;
SELECT COUNT(*) FROM ml_clusterization;
SELECT COUNT(*) FROM ml_recommendation;

-- Análise de classificação
SELECT potencial_recompra, COUNT(*) as total
FROM ml_classification
GROUP BY potencial_recompra;

-- Análise de clusters
SELECT cluster, COUNT(*) as total
FROM ml_clusterization
GROUP BY cluster;

-- Top rotas recomendadas
SELECT predicted_route_1, COUNT(*) as freq
FROM ml_recommendation
GROUP BY predicted_route_1
ORDER BY freq DESC
LIMIT 10;
```

## Manutenção

- **Logs**: Rotacione o arquivo `ml_data_load.log` periodicamente
- **Índices**: Monitor performance e ajuste índices conforme padrões de consulta
- **Backup**: Configure backup regular das tabelas ML
- **Atualizações**: Re-execute quando novos modelos forem treinados
