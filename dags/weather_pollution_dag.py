from airflow.decorators import dag, task
from datetime import datetime, timedelta

default_args = {
    'owner': 'victor',
    'retries': 1,
    'retry_delay': timedelta(minutes=3),
}

@dag(
    dag_id='pipeline_poluicao',
    default_args=default_args,
    description='Pipeline de previsão do tempo via OpenWeather',
    schedule_interval='@hourly',
    start_date=datetime(2024, 5, 1),
    catchup=False,
    tags=['weather', 'pollution'],
    params={"city": "Londrina"},  # ✅ default aqui

)
def weather_pollution_etl():

    @task()
    def extrair():
        from pipelines.pollution.extract import extract_pollution
        return extract_pollution(city="São Paulo")

    @task()
    def transformar(collected_at):
        from pipelines.pollution.transform import transform_pollution
        return transform_pollution(city="São Paulo", collected_at=collected_at)

    @task()
    def carregar(df):
        from pipelines.pollution.load import load_pollution
        return load_pollution(df=df)

    tempo_coleta = extrair()
    dados = transformar(tempo_coleta)
    carregar(dados)

dag_instance = weather_pollution_etl()