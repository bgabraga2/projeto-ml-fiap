#!/usr/bin/env python3
"""
Script de teste para a API de Machine Learning

Este script testa todos os endpoints da API com dados REAIS extraídos dos datasets dos modelos:
- Clusterização: Features comportamentais calculadas baseadas em transações reais
- Classificação: Dados históricos de cliente real com 666 dias desde última compra
- Recomendação: Transação real de 2018-12-05 do dataset de clusterização
"""

import requests
import json
import time

# URL base da API
BASE_URL = "http://localhost:3021"

def test_health():
    """Testa o endpoint de saúde"""
    print("🔍 Testando endpoint /health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Resposta: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_root():
    """Testa o endpoint raiz"""
    print("\n🔍 Testando endpoint /...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Resposta: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_clusterization():
    """Testa o endpoint de clusterização"""
    print("\n🔍 Testando endpoint /clusterization...")
    
    # Dados reais baseados no dataset de clusterização
    # Representa um cliente com comportamento médio-baixo
    payload = {
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
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/clusterization",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Resposta: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_classification():
    """Testa o endpoint de classificação"""
    print("\n🔍 Testando endpoint /classification...")
    
    # Dados reais do dataset de classificação (cliente com histórico real)
    # Cliente com 666 dias desde última compra - baixa probabilidade de recompra
    payload = {
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
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/classification",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Resposta: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_recommendation():
    """Testa o endpoint de recomendação"""
    print("\n🔍 Testando endpoint /recommendation...")
    
    # Dados reais do dataset de recomendação (transação real)
    # Transação de dezembro de 2018 - viagem de ida e volta
    payload = {
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
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/recommendation",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Resposta: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_edge_cases():
    """Testa casos extremos com dados reais variados"""
    print("\n🔍 Testando casos extremos com dados reais...")
    
    # Teste com cliente de alta frequência (cluster 2)
    # Cliente premium com GMV alto e múltiplas compras
    high_freq_payload = {
        "gmv_mean": 264.25,
        "gmv_total": 2578.4,
        "purchase_count": 15,
        "gmv_std": 166.05,
        "tickets_mean": 1.92,
        "tickets_total": 29,
        "tickets_std": 0.8,
        "round_trip_rate": 1.0,
        "weekend_rate": 0.23,
        "preferred_day": 1,
        "avg_hour": 14.55,
        "preferred_month": 7,
        "avg_company_freq": 69493.0
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/clusterization",
            json=high_freq_payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Teste cluster alta frequência - Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Cluster previsto: {result.get('cluster')} (esperado: 2 - Alto Valor)")
            print(f"Confiança: {result.get('confidence', 0):.3f}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro no teste de casos extremos: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🚀 Iniciando testes da API ML Models com DADOS REAIS...")
    print("=" * 70)
    print("📊 Dados extraídos dos datasets reais dos modelos treinados")
    print("=" * 70)
    
    # Aguardar um pouco caso a API esteja iniciando
    print("⏳ Aguardando API inicializar...")
    time.sleep(2)
    
    tests = [
        ("Health Check", test_health),
        ("Root Endpoint", test_root),
        ("Clusterização", test_clusterization),
        ("Classificação", test_classification),
        ("Recomendação", test_recommendation),
        ("Casos Extremos", test_edge_cases)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        success = test_func()
        results.append((test_name, success))
        if success:
            print("✅ Teste passou!")
        else:
            print("❌ Teste falhou!")
    
    # Resumo final
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{test_name:20} | {status}")
        if success:
            passed += 1
    
    print(f"\nResultado: {passed}/{len(tests)} testes passaram")
    
    if passed == len(tests):
        print("🎉 Todos os testes passaram! API funcionando corretamente.")
    else:
        print("⚠️  Alguns testes falharam. Verifique os logs acima.")
    
    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
