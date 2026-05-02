from airflow.decorators import dag, task
from datetime import datetime, timedelta
import logging

# Importando as suas funções diretamente!
from pipelines.current.extract import extract_current
from pipelines.current.transform import transform_current
from pipelines.current.load import load_current

logger = logging.getLogger(__name__)

# Configurações padrão para todas as tarefas desta DAG
default_args = {
    'owner': 'victor',
    'depends_on_past': False,
    'retries': 1, # Tenta novamente 1 vez se falhar (útil para APIs instáveis)
    'retry_delay': timedelta(minutes=3),
}

@dag(
    dag_id='pipeline_tempo_atual', # O nome que vai aparecer no painel do Airflow
    default_args=default_args,
    description='Pipeline de extração do tempo atual via OpenWeather',
    schedule_interval='@hourly', # Roda a cada 1 hora
    start_date=datetime(2024, 5, 1),
    catchup=False, # Não tenta rodar o passado
    tags=['weather', 'current'],
)
def weather_current_etl():

    # 1. Tarefa de Extração
    @task()
    def extrair():
        # Retorna o datetime da coleta
        return extract_current(city="São Paulo")

    # 2. Tarefa de Transformação
    @task()
    def transformar(collected_at: datetime):
        # Recebe o collected_at e retorna o DataFrame
        return transform_current(city="São Paulo", collected_at=collected_at)

    # 3. Tarefa de Carga
    @task()
    def carregar(df):
        # Recebe o DataFrame e faz a inserção
        return load_current(df=df)

    # --- Orquestração (Definindo a ordem) ---
    tempo_coleta = extrair()
    dados_transformados = transformar(tempo_coleta)
    carregar(dados_transformados)

# Instanciando a DAG
dag_instance = weather_current_etl()