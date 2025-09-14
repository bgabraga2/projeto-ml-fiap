"""
API FastAPI para servir três modelos de Machine Learning:
1. Clusterização de clientes
2. Classificação de recompra em 30 dias
3. Recomendação de rotas

Desenvolvido por: Desenvolvedor Python Sênior
Data: 2025
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import pickle
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicialização da aplicação FastAPI
app = FastAPI(
    title="ML Models API",
    description="API para servir modelos de Machine Learning: Clusterização, Classificação e Recomendação",
    version="1.0.0"
)

# Caminhos para os modelos versionados
MODEL_VERSION = "v1"
# Ajustar caminhos para funcionar tanto local quanto no Docker
BASE_PATH = "artefacts" if os.path.exists("artefacts") else "../artefacts"
MODEL_PATHS = {
    "clusterization": f"{BASE_PATH}/{MODEL_VERSION}/clusterization/modelo_clusterizacao.pkl",
    "classification": f"{BASE_PATH}/{MODEL_VERSION}/classification/modelo_recompra_30dias.pkl",
    "recommendation": {
        "model": f"{BASE_PATH}/{MODEL_VERSION}/recommendation/modelo_recomendacao.pkl",
        "label_encoder": f"{BASE_PATH}/{MODEL_VERSION}/recommendation/label_encoder.pkl",
        "feature_encoders": f"{BASE_PATH}/{MODEL_VERSION}/recommendation/feature_encoders.pkl"
    }
}

# Cache para modelos carregados - evita recarregar modelos pesados a cada requisição
model_cache = {}

# ============================================================================
# MODELOS DE ENTRADA (PYDANTIC SCHEMAS)
# ============================================================================

class ClusterizationInput(BaseModel):
    """Schema de entrada para o modelo de clusterização"""
    gmv_mean: float = Field(..., description="Valor médio das compras (GMV)")
    gmv_total: float = Field(..., description="Valor total das compras (GMV)")
    purchase_count: int = Field(..., description="Número total de compras")
    gmv_std: float = Field(..., description="Desvio padrão do GMV")
    tickets_mean: float = Field(..., description="Média de tickets por compra")
    tickets_total: int = Field(..., description="Total de tickets comprados")
    tickets_std: float = Field(..., description="Desvio padrão dos tickets")
    round_trip_rate: float = Field(..., description="Taxa de viagens de ida e volta")
    weekend_rate: float = Field(..., description="Taxa de compras em fins de semana")
    preferred_day: int = Field(..., description="Dia da semana preferido (0-6)")
    avg_hour: float = Field(..., description="Hora média das compras")
    preferred_month: int = Field(..., description="Mês preferido (1-12)")
    avg_company_freq: float = Field(..., description="Frequência média da empresa")

    class Config:
        json_schema_extra = {
            "example": {
                "gmv_mean": 150.50,
                "gmv_total": 300.75,
                "purchase_count": 3,
                "gmv_std": 25.30,
                "tickets_mean": 1.2,
                "tickets_total": 4,
                "tickets_std": 0.5,
                "round_trip_rate": 1.0,
                "weekend_rate": 0.1,
                "preferred_day": 2,
                "avg_hour": 14.5,
                "preferred_month": 6,
                "avg_company_freq": 100.0
            }
        }

class ClassificationInput(BaseModel):
    """Schema de entrada para o modelo de classificação"""
    gmv_ultima_compra: float = Field(..., description="GMV da última compra")
    tickets_ultima_compra: int = Field(..., description="Tickets da última compra")
    origem_ultima: str = Field(..., description="Origem da última viagem")
    destino_ultima: str = Field(..., description="Destino da última viagem")
    empresa_ultima: str = Field(..., description="Empresa da última viagem")
    dias_desde_ultima_compra: int = Field(..., description="Dias desde a última compra")
    total_compras: int = Field(..., description="Total de compras históricas")
    dias_unicos_compra: int = Field(..., description="Dias únicos com compras")
    gmv_total: float = Field(..., description="GMV total histórico")
    gmv_medio: float = Field(..., description="GMV médio")
    gmv_std: float = Field(..., description="Desvio padrão do GMV")
    gmv_min: float = Field(..., description="GMV mínimo")
    gmv_max: float = Field(..., description="GMV máximo")
    tickets_total: int = Field(..., description="Total de tickets")
    tickets_medio: float = Field(..., description="Média de tickets")
    tickets_max: int = Field(..., description="Máximo de tickets")
    mes_preferido: int = Field(..., description="Mês preferido")
    dia_semana_preferido: int = Field(..., description="Dia da semana preferido")
    hora_media: float = Field(..., description="Hora média das compras")
    hora_std: float = Field(..., description="Desvio padrão da hora")
    origens_unicas: int = Field(..., description="Número de origens únicas")
    destinos_unicos: int = Field(..., description="Número de destinos únicos")
    empresas_unicas: int = Field(..., description="Número de empresas únicas")
    intervalo_medio_dias: float = Field(..., description="Intervalo médio entre compras")
    regularidade: float = Field(..., description="Regularidade das compras")

    class Config:
        json_schema_extra = {
            "example": {
                "gmv_ultima_compra": 120.50,
                "tickets_ultima_compra": 1,
                "origem_ultima": "origem_hash_123",
                "destino_ultima": "destino_hash_456",
                "empresa_ultima": "empresa_hash_789",
                "dias_desde_ultima_compra": 15,
                "total_compras": 5,
                "dias_unicos_compra": 4,
                "gmv_total": 600.25,
                "gmv_medio": 120.05,
                "gmv_std": 25.30,
                "gmv_min": 85.00,
                "gmv_max": 150.75,
                "tickets_total": 6,
                "tickets_medio": 1.2,
                "tickets_max": 2,
                "mes_preferido": 7,
                "dia_semana_preferido": 1,
                "hora_media": 14.5,
                "hora_std": 2.1,
                "origens_unicas": 2,
                "destinos_unicos": 3,
                "empresas_unicas": 2,
                "intervalo_medio_dias": 30.5,
                "regularidade": 5.2
            }
        }

class RecommendationInput(BaseModel):
    """Schema de entrada para o modelo de recomendação"""
    fk_contact: str = Field(..., description="ID do contato")
    date_purchase: str = Field(..., description="Data da compra (YYYY-MM-DD)")
    time_purchase: str = Field(..., description="Hora da compra (HH:MM:SS)")
    place_origin_departure: str = Field(..., description="Local de origem")
    place_destination_departure: str = Field(..., description="Local de destino")
    place_origin_return: str = Field(..., description="Local de origem do retorno")
    place_destination_return: str = Field(..., description="Local de destino do retorno")
    fk_departure_ota_bus_company: str = Field(..., description="Empresa de ônibus")
    fk_return_ota_bus_company: str = Field(..., description="Empresa de ônibus retorno")
    gmv_success: float = Field(..., description="GMV da transação")
    total_tickets_quantity_success: int = Field(..., description="Quantidade de tickets")
    route_departure: str = Field(..., description="Rota de ida")
    route_return: str = Field(..., description="Rota de volta")
    is_round_trip: int = Field(..., description="Viagem de ida e volta (0 ou 1)")
    departure_company_freq: int = Field(..., description="Frequência da empresa")
    return_company_freq: int = Field(..., description="Frequência da empresa retorno")
    origin_dept_freq: int = Field(..., description="Frequência da origem")
    dest_dept_freq: int = Field(..., description="Frequência do destino")
    route_departure_freq: int = Field(..., description="Frequência da rota")
    cluster: int = Field(..., description="Cluster do cliente")

    class Config:
        json_schema_extra = {
            "example": {
                "fk_contact": "contact_hash_123",
                "date_purchase": "2024-01-15",
                "time_purchase": "14:30:00",
                "place_origin_departure": "origin_hash_456",
                "place_destination_departure": "dest_hash_789",
                "place_origin_return": "0",
                "place_destination_return": "0",
                "fk_departure_ota_bus_company": "company_hash_abc",
                "fk_return_ota_bus_company": "1",
                "gmv_success": 125.50,
                "total_tickets_quantity_success": 1,
                "route_departure": "route_hash_def",
                "route_return": "0_to_0",
                "is_round_trip": 1,
                "departure_company_freq": 1500,
                "return_company_freq": 1000000,
                "origin_dept_freq": 5000,
                "dest_dept_freq": 3000,
                "route_departure_freq": 250,
                "cluster": 2
            }
        }

# ============================================================================
# MODELOS DE SAÍDA (PYDANTIC SCHEMAS)
# ============================================================================

class ClusterizationOutput(BaseModel):
    """Schema de saída para o modelo de clusterização"""
    cluster: int = Field(..., description="Cluster identificado")
    cluster_profile: Dict[str, Any] = Field(..., description="Perfil do cluster")
    confidence: float = Field(..., description="Confiança da predição")

class ClassificationOutput(BaseModel):
    """Schema de saída para o modelo de classificação"""
    will_purchase: bool = Field(..., description="Probabilidade de compra (true/false)")
    probability: float = Field(..., description="Probabilidade numérica (0-1)")
    risk_category: str = Field(..., description="Categoria de risco")

class RecommendationOutput(BaseModel):
    """Schema de saída para o modelo de recomendação"""
    top_3_routes: List[Dict[str, Any]] = Field(..., description="Top 3 rotas recomendadas")
    user_cluster: int = Field(..., description="Cluster do usuário")

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def load_model(model_type: str):
    """
    Carrega um modelo do cache ou do disco
    Implementa lazy loading - só carrega quando necessário
    """
    if model_type in model_cache:
        return model_cache[model_type]
    
    try:
        if model_type == "clusterization":
            with open(MODEL_PATHS["clusterization"], 'rb') as f:
                model_data = pickle.load(f)
            model_cache[model_type] = model_data
            
        elif model_type == "classification":
            with open(MODEL_PATHS["classification"], 'rb') as f:
                model_data = pickle.load(f)
            model_cache[model_type] = model_data
            
        elif model_type == "recommendation":
            models = {}
            # Carregar modelo principal
            with open(MODEL_PATHS["recommendation"]["model"], 'rb') as f:
                models["model"] = pickle.load(f)
            # Carregar label encoder
            with open(MODEL_PATHS["recommendation"]["label_encoder"], 'rb') as f:
                models["label_encoder"] = pickle.load(f)
            # Carregar feature encoders
            with open(MODEL_PATHS["recommendation"]["feature_encoders"], 'rb') as f:
                models["feature_encoders"] = pickle.load(f)
            model_cache[model_type] = models
            
        return model_cache[model_type]
        
    except Exception as e:
        logger.error(f"Erro ao carregar modelo {model_type}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao carregar modelo {model_type}")

def create_cluster_profile(cluster_id: int) -> Dict[str, Any]:
    """
    Cria o perfil de um cluster baseado nos dados conhecidos
    Perfis extraídos da análise dos clusters reais do modelo K-Means
    """
    cluster_profiles = {
        0: {
            "description": "Clientes Regulares - Baixo Valor",
            "characteristics": {
                "gmv_mean": 143.12,
                "purchase_frequency": "Baixa-Média",
                "behavior": "Compras esporádicas, valores médios baixos"
            }
        },
        1: {
            "description": "Clientes Fins de Semana",
            "characteristics": {
                "gmv_mean": 139.4,
                "purchase_frequency": "Média",
                "behavior": "Preferem comprar nos fins de semana"
            }
        },
        2: {
            "description": "Clientes Frequentes - Alto Valor",
            "characteristics": {
                "gmv_mean": 264.25,
                "purchase_frequency": "Alta",
                "behavior": "Compras frequentes, valores altos"
            }
        },
        3: {
            "description": "Clientes VIP - Altíssimo Volume",
            "characteristics": {
                "gmv_mean": 260.21,
                "purchase_frequency": "Muito Alta",
                "behavior": "Clientes excepcionais, volume muito alto"
            }
        },
        4: {
            "description": "Clientes Premium - Tickets Múltiplos",
            "characteristics": {
                "gmv_mean": 544.22,
                "purchase_frequency": "Baixa",
                "behavior": "Compras de alto valor com múltiplos tickets"
            }
        }
    }
    return cluster_profiles.get(cluster_id, {"description": "Cluster Desconhecido", "characteristics": {}})

def process_datetime_features(date_str: str, time_str: str) -> Dict[str, Any]:
    """
    Processa features de data e hora para o modelo de recomendação
    Extrai características temporais que influenciam padrões de viagem
    """
    try:
        # Limpar time_str se contém data prefixada
        if "1900-01-01" in time_str:
            time_str = time_str.split(" ")[1]
        
        dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
        
        # Mapear period_of_day para números diretamente
        # Períodos do dia influenciam preferências de viagem
        hour = dt.hour
        if 6 <= hour < 12:
            period_num = 0  # manhã - viagens de trabalho
        elif 12 <= hour < 18:
            period_num = 1  # tarde - viagens de lazer/retorno
        elif 18 <= hour < 22:
            period_num = 2  # noite - viagens de final de expediente
        else:
            period_num = 3  # madrugada - viagens especiais/emergência
        
        return {
            "day_of_week": int(dt.weekday()),
            "month": int(dt.month),
            "quarter": int((dt.month - 1) // 3 + 1),
            "is_weekend": int(1 if dt.weekday() >= 5 else 0),
            "hour": int(dt.hour),
            "period_of_day": period_num  # Já como número
        }
    except Exception as e:
        logger.warning(f"Erro ao processar datetime {date_str} {time_str}: {e}")
        # Valores padrão em caso de erro
        return {
            "day_of_week": 0,
            "month": 1,
            "quarter": 1,
            "is_weekend": 0,
            "hour": 12,
            "period_of_day": 1  # afternoon
        }

# ============================================================================
# ENDPOINTS DA API
# ============================================================================

@app.get("/")
async def root():
    """Endpoint raiz com informações da API"""
    return {
        "message": "ML Models API",
        "version": "1.0.0",
        "endpoints": [
            "/clusterization - Segmentação de clientes",
            "/classification - Predição de recompra",
            "/recommendation - Recomendação de rotas"
        ]
    }

@app.post("/clusterization", response_model=ClusterizationOutput)
async def predict_cluster(input_data: ClusterizationInput):
    """
    Endpoint para predição de cluster de cliente
    
    Recebe dados comportamentais do cliente e retorna o cluster identificado
    """
    try:
        # Carregar modelo
        model_data = load_model("clusterization")
        model = model_data["model"]
        scaler = model_data["scaler"]
        
        # Preparar dados de entrada com nomes de colunas
        feature_names = [
            "gmv_mean", "gmv_total", "purchase_count", "gmv_std",
            "tickets_mean", "tickets_total", "tickets_std",
            "round_trip_rate", "weekend_rate", "preferred_day",
            "avg_hour", "preferred_month", "avg_company_freq"
        ]
        
        features_dict = {
            "gmv_mean": input_data.gmv_mean,
            "gmv_total": input_data.gmv_total,
            "purchase_count": input_data.purchase_count,
            "gmv_std": input_data.gmv_std,
            "tickets_mean": input_data.tickets_mean,
            "tickets_total": input_data.tickets_total,
            "tickets_std": input_data.tickets_std,
            "round_trip_rate": input_data.round_trip_rate,
            "weekend_rate": input_data.weekend_rate,
            "preferred_day": input_data.preferred_day,
            "avg_hour": input_data.avg_hour,
            "preferred_month": input_data.preferred_month,
            "avg_company_freq": input_data.avg_company_freq
        }
        
        # Criar DataFrame com nomes de colunas
        features_df = pd.DataFrame([features_dict])
        
        # Normalizar features - K-Means é sensível à escala das variáveis
        features_scaled = scaler.transform(features_df)
        
        # Fazer predição do cluster
        cluster_pred = model.predict(features_scaled)[0]
        
        # Calcular distâncias para medir confiança
        # Menor distância ao centroide = maior confiança na classificação
        distances = model.transform(features_scaled)[0]
        confidence = 1.0 / (1.0 + min(distances))
        
        # Criar perfil do cluster
        cluster_profile = create_cluster_profile(cluster_pred)
        
        return ClusterizationOutput(
            cluster=int(cluster_pred),
            cluster_profile=cluster_profile,
            confidence=float(confidence)
        )
        
    except Exception as e:
        logger.error(f"Erro na predição de cluster: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro na predição: {str(e)}")

@app.post("/classification", response_model=ClassificationOutput)
async def predict_purchase(input_data: ClassificationInput):
    """
    Endpoint para predição de recompra em 30 dias
    
    Recebe dados históricos do cliente e retorna probabilidade de recompra
    """
    try:
        # Carregar modelo
        model_data = load_model("classification")
        model = model_data["model"]
        feature_columns = model_data["feature_columns"]
        label_encoders = model_data.get("label_encoders", {})
        
        # Preparar dados em formato DataFrame
        data_dict = input_data.dict()
        
        # Aplicar label encoders para variáveis categóricas (origem, destino, empresa)
        # Tratamento defensivo para valores não vistos durante treinamento
        for col, encoder in label_encoders.items():
            if col in data_dict:
                try:
                    # Tentar transformar usando o encoder
                    str_value = str(data_dict[col])
                    if hasattr(encoder, 'classes_') and str_value in encoder.classes_:
                        data_dict[col] = encoder.transform([str_value])[0]
                    else:
                        # Se valor não existe no encoder, usar valor padrão
                        # Evita erro em dados não vistos no treinamento
                        data_dict[col] = 0
                except Exception as e:
                    logger.warning(f"Erro ao codificar {col} na classificação: {e}. Usando valor padrão.")
                    data_dict[col] = 0
        
        # Criar DataFrame com as features na ordem correta
        df = pd.DataFrame([data_dict])
        
        # Garantir que todas as features estão presentes
        for col in feature_columns:
            if col not in df.columns:
                df[col] = 0
        
        # Selecionar apenas as colunas do modelo
        X = df[feature_columns]
        
        # Fazer predição de recompra em 30 dias
        probability = model.predict_proba(X)[0][1]  # Probabilidade da classe positiva (vai comprar)
        prediction = probability > 0.5
        
        # Determinar categoria de risco baseada na probabilidade
        # Thresholds definidos para ações de marketing diferenciadas
        if probability >= 0.6:
            risk_category = "Alto"    # Cliente muito provável de comprar - ofertas premium
        elif probability >= 0.3:
            risk_category = "Médio"   # Cliente moderado - campanhas direcionadas
        else:
            risk_category = "Baixo"   # Cliente improvável - campanhas de reativação
        
        return ClassificationOutput(
            will_purchase=bool(prediction),
            probability=float(probability),
            risk_category=risk_category
        )
        
    except Exception as e:
        logger.error(f"Erro na predição de classificação: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro na predição: {str(e)}")

@app.post("/recommendation", response_model=RecommendationOutput)
async def recommend_routes(input_data: RecommendationInput):
    """
    Endpoint para recomendação de rotas
    
    Recebe dados da viagem atual e retorna top 3 rotas recomendadas
    """
    try:
        # Carregar modelos
        models = load_model("recommendation")
        model = models["model"]
        label_encoder = models["label_encoder"]
        feature_encoders = models["feature_encoders"]
        
        # Preparar dados de entrada
        data_dict = input_data.dict()
        
        # Processar features de data/hora
        datetime_features = process_datetime_features(
            data_dict["date_purchase"], 
            data_dict["time_purchase"]
        )
        data_dict.update(datetime_features)
        
        # Adicionar features de metadata que podem estar faltando
        if 'data_clusterizacao' not in data_dict:
            data_dict['data_clusterizacao'] = datetime.now().strftime('%Y-%m-%d')
        if 'versao_modelo' not in data_dict:
            data_dict['versao_modelo'] = 'XGBoost_v1.0'
        
        # Aplicar encoders para features categóricas
        for col, encoder in feature_encoders.items():
            if col in data_dict:
                try:
                    # Converter para string e aplicar encoder
                    str_value = str(data_dict[col])
                    if hasattr(encoder, 'classes_') and str_value in encoder.classes_:
                        data_dict[col] = int(encoder.transform([str_value])[0])  # Garantir int
                    else:
                        # Se valor não existe no encoder, usar valor padrão
                        data_dict[col] = 0
                except Exception as e:
                    logger.warning(f"Erro ao codificar {col}: {e}. Usando valor padrão.")
                    data_dict[col] = 0
        
        # Forçar conversão de campos específicos que podem ser problemáticos
        # XGBoost requer que todas as features sejam numéricas
        # Campos categóricos já foram processados pelos encoders
        problem_fields = {
            'fk_contact': str,
            'place_origin_return': str, 
            'place_destination_return': str,
            'fk_return_ota_bus_company': str,
            'date_purchase': str,
            'time_purchase': str,
            'data_clusterizacao': str,
            'versao_modelo': str
        }
        
        for field, expected_type in problem_fields.items():
            if field in data_dict:
                try:
                    # Se é string, tentar converter para hash numérico ou valor padrão
                    if isinstance(data_dict[field], str):
                        if field in ['place_origin_return', 'place_destination_return']:
                            # Estes geralmente são "0" como string
                            data_dict[field] = 0 if data_dict[field] == "0" else hash(data_dict[field]) % 10000
                        elif field == 'fk_return_ota_bus_company':
                            # Geralmente "1" como string
                            data_dict[field] = 1 if data_dict[field] == "1" else int(pd.to_numeric(data_dict[field], errors='coerce'))
                        elif field in ['data_clusterizacao', 'versao_modelo']:
                            # Para campos de metadata, usar hash consistente
                            data_dict[field] = abs(hash(data_dict[field])) % 10000
                        else:
                            # Para outros campos string, usar hash
                            data_dict[field] = abs(hash(data_dict[field])) % 100000
                    else:
                        # Se já é numérico, garantir que é int
                        data_dict[field] = int(pd.to_numeric(data_dict[field], errors='coerce'))
                except:
                    data_dict[field] = 0
        
        # Converter para DataFrame
        df = pd.DataFrame([data_dict])
        
        # Garantir que todas as features necessárias estão presentes
        required_features = [
            'fk_contact', 'date_purchase', 'time_purchase', 'place_origin_departure',
            'place_destination_departure', 'place_origin_return', 'place_destination_return',
            'fk_departure_ota_bus_company', 'fk_return_ota_bus_company', 'gmv_success',
            'total_tickets_quantity_success', 'day_of_week', 'month', 'quarter',
            'is_weekend', 'hour', 'period_of_day', 'route_departure', 'route_return',
            'is_round_trip', 'departure_company_freq', 'return_company_freq',
            'origin_dept_freq', 'dest_dept_freq', 'route_departure_freq', 'cluster',
            'data_clusterizacao', 'versao_modelo'
        ]
        
        for feature in required_features:
            if feature not in df.columns:
                # Adicionar valores padrão apropriados para as features faltantes
                if feature == 'data_clusterizacao':
                    # Data de clusterização - usar data atual formatada
                    df[feature] = datetime.now().strftime('%Y-%m-%d')
                elif feature == 'versao_modelo':
                    # Versão do modelo - usar valor padrão
                    df[feature] = 'XGBoost_v1.0'
                else:
                    df[feature] = 0
        
        # Converter colunas object para numeric para XGBoost
        object_columns = ['fk_contact', 'place_origin_return', 'place_destination_return', 
                         'fk_return_ota_bus_company', 'data_clusterizacao', 'versao_modelo']
        
        for col in object_columns:
            if col in df.columns:
                # Converter object para numeric
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        # Garantir que todas as colunas são numéricas
        for col in required_features:
            if col in df.columns:
                if df[col].dtype == 'object':
                    logger.warning(f"Convertendo coluna {col} de object para numeric")
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        # Debug: verificar tipos das colunas
        object_cols = [col for col in df[required_features].columns if df[col].dtype == 'object']
        if object_cols:
            logger.error(f"Colunas ainda em object: {object_cols}")
            # Forçar conversão final
            for col in object_cols:
                df[col] = 0  # Valor padrão seguro
        
        # Fazer predição - obter probabilidades para todas as rotas possíveis
        probabilities = model.predict_proba(df[required_features])[0]
        
        # Obter top 3 rotas com maior probabilidade
        # Ordenação decrescente das probabilidades
        top_3_indices = np.argsort(probabilities)[-3:][::-1]
        
        # Converter índices de volta para rotas originais usando label encoder
        top_3_routes = []
        for i, idx in enumerate(top_3_indices):
            route_encoded = label_encoder.inverse_transform([idx])[0]
            
            # Tentar decodificar a rota usando o encoder de features
            route_original = route_encoded
            if "route_departure" in feature_encoders:
                try:
                    route_original = feature_encoders["route_departure"].inverse_transform([route_encoded])[0]
                except:
                    route_original = str(route_encoded)
            
            top_3_routes.append({
                "rank": i + 1,
                "route": str(route_original),
                "probability": float(probabilities[idx]),
                "confidence": float(probabilities[idx] * 100)
            })
        
        return RecommendationOutput(
            top_3_routes=top_3_routes,
            user_cluster=int(input_data.cluster)
        )
        
    except Exception as e:
        logger.error(f"Erro na recomendação: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro na recomendação: {str(e)}")

# ============================================================================
# ENDPOINT DE SAÚDE
# ============================================================================

@app.get("/health")
async def health_check():
    """Endpoint para verificar a saúde da API"""
    try:
        # Verificar se os arquivos de modelo existem
        model_status = {}
        
        # Verificar clusterização
        model_status["clusterization"] = os.path.exists(MODEL_PATHS["clusterization"])
        
        # Verificar classificação
        model_status["classification"] = os.path.exists(MODEL_PATHS["classification"])
        
        # Verificar recomendação
        model_status["recommendation"] = all([
            os.path.exists(MODEL_PATHS["recommendation"]["model"]),
            os.path.exists(MODEL_PATHS["recommendation"]["label_encoder"]),
            os.path.exists(MODEL_PATHS["recommendation"]["feature_encoders"])
        ])
        
        all_healthy = all(model_status.values())
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "timestamp": datetime.now().isoformat(),
            "models": model_status,
            "cache_status": {
                "loaded_models": list(model_cache.keys()),
                "cache_size": len(model_cache)
            }
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ============================================================================
# INICIALIZAÇÃO
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Pré-carregar modelos para melhor performance (warm-up)
    # Evita latência na primeira requisição de cada modelo
    logger.info("Iniciando API e pré-carregando modelos...")
    
    try:
        load_model("clusterization")
        logger.info("✓ Modelo de clusterização carregado")
    except Exception as e:
        logger.error(f"✗ Erro ao carregar modelo de clusterização: {e}")
    
    try:
        load_model("classification")
        logger.info("✓ Modelo de classificação carregado")
    except Exception as e:
        logger.error(f"✗ Erro ao carregar modelo de classificação: {e}")
    
    try:
        load_model("recommendation")
        logger.info("✓ Modelo de recomendação carregado")
    except Exception as e:
        logger.error(f"✗ Erro ao carregar modelo de recomendação: {e}")
    
    # Iniciar servidor
    uvicorn.run(app, host="0.0.0.0", port=3021)
