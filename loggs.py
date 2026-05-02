import os
import logging
from datetime import datetime, timedelta

PASTA_LOGS = 'logs'
DIAS_RETENCAO = 7  # apaga logs mais velhos que 7 dias

def limpar_logs_antigos():
    limite = datetime.now() - timedelta(days=DIAS_RETENCAO)
    for arquivo in os.listdir(PASTA_LOGS):
        caminho = os.path.join(PASTA_LOGS, arquivo)
        if not arquivo.endswith('.log'):
            continue
        data_modificacao = datetime.fromtimestamp(os.path.getmtime(caminho))
        if data_modificacao < limite:
            os.remove(caminho)
            print(f"Log removido: {arquivo}")

if not os.path.exists(PASTA_LOGS):
    os.makedirs(PASTA_LOGS)

limpar_logs_antigos()  # roda na inicialização

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
nome_arquivo_log = f'log_{timestamp}.log'

logging.basicConfig(
    filename=os.path.join(PASTA_LOGS, nome_arquivo_log),
    level=logging.ERROR,
    force=True,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S",
    encoding='utf-8'
)