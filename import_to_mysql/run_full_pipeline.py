#!/usr/bin/env python3
"""
Pipeline completo para carregamento e verificação dos dados ML no MySQL
Executa o carregamento e em seguida a verificação de integridade
"""

import subprocess
import sys
import logging
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_script(script_name: str) -> bool:
    """
    Executa um script Python e retorna se foi bem-sucedido
    
    Args:
        script_name: Nome do script para executar
        
    Returns:
        bool: True se executou com sucesso, False caso contrário
    """
    try:
        logger.info(f"Executando {script_name}...")
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"✅ {script_name} executado com sucesso")
            return True
        else:
            logger.error(f"❌ {script_name} falhou com código {result.returncode}")
            logger.error(f"Erro: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao executar {script_name}: {e}")
        return False

def main():
    """Função principal do pipeline"""
    start_time = datetime.now()
    
    logger.info("🚀 === INICIANDO PIPELINE COMPLETO DE DADOS ML ===")
    
    # Lista de scripts para executar em ordem
    scripts = [
        'load_ml_datasets_to_mysql.py',
        'verify_data_integrity.py'
    ]
    
    success = True
    
    for script in scripts:
        if not run_script(script):
            success = False
            break
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    if success:
        logger.info("🎉 === PIPELINE CONCLUÍDO COM SUCESSO ===")
        logger.info(f"⏱️ Tempo total: {duration}")
        logger.info("📊 Dados ML carregados e verificados no MySQL")
        logger.info("🔍 Consulte os logs detalhados em ml_data_load.log")
    else:
        logger.error("💥 === PIPELINE FALHOU ===")
        logger.error(f"⏱️ Tempo até falha: {duration}")
        logger.error("🔧 Verifique os logs e configurações antes de tentar novamente")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
