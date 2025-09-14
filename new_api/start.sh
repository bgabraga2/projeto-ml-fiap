#!/bin/bash

# Script para inicializar a API ML Models
echo "🚀 Iniciando API ML Models..."

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Por favor, instale Python 3.8+"
    exit 1
fi

# Verificar se pip está instalado
if ! command -v pip &> /dev/null; then
    echo "❌ pip não encontrado. Por favor, instale pip"
    exit 1
fi

# Remover ambiente virtual antigo se existir com problemas
if [ -d "venv" ] && [ -f "venv/pyvenv.cfg" ]; then
    echo "🔄 Verificando ambiente virtual existente..."
    source venv/bin/activate 2>/dev/null || {
        echo "⚠️  Ambiente virtual corrompido. Recriando..."
        rm -rf venv
    }
    deactivate 2>/dev/null || true
fi

# Criar novo ambiente virtual se necessário
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

echo "📥 Atualizando pip..."
pip install --upgrade pip setuptools wheel

echo "📥 Instalando dependências..."
pip install --no-cache-dir -r requirements.txt

echo "🔍 Verificando se os modelos existem..."
# Validação crítica - API não funciona sem os modelos treinados
if [ ! -f "../dist/clusterization/artifacts/modelo_clusterizacao.pkl" ]; then
    echo "❌ Modelo de clusterização não encontrado em ../dist/clusterization/artifacts/"
    echo "Execute os notebooks de treinamento primeiro!"
    exit 1
fi

if [ ! -f "../dist/classification/artifacts/modelo_recompra_30dias.pkl" ]; then
    echo "❌ Modelo de classificação não encontrado em ../dist/classification/artifacts/"
    echo "Execute os notebooks de treinamento primeiro!"
    exit 1
fi

if [ ! -f "../dist/recommendation/artifacts/modelo_recomendacao.pkl" ]; then
    echo "❌ Modelo de recomendação não encontrado em ../dist/recommendation/artifacts/"
    echo "Execute os notebooks de treinamento primeiro!"
    exit 1
fi

echo "✅ Todos os modelos encontrados!"
echo "🌐 Iniciando servidor na porta 3021..."
echo ""

python main.py
