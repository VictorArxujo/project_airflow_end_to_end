from airflow.decorators import dag, task
from datetime import datetime, timedelta

default_args = {
    'owner': 'victor',
    'retries': 1,
    'retry_delay': timedelta(minutes=3),
}

@dag(
    dag_id='pipeline_tempo_atual',
    default_args=default_args,
    description='Pipeline de extração do tempo atual via OpenWeather',
    schedule_interval='@hourly',
    start_date=datetime(2024, 5, 1),
    catchup=False,
    tags=['weather', 'current'],
    params={"city": "Londrina"},  # ✅ default aqui
)
def weather_current_etl():

    @task()
    def extrair(**context):
        city = context["params"]["city"]  # ✅ pega o param
        from pipelines.current.extract import extract_current
        return extract_current(city=city)

    @task()
    def transformar(collected_at, **context):
        city = context["params"]["city"]
        from pipelines.current.transform import transform_current
        df = transform_current(city=city, collected_at=collected_at)
        return df.to_dict(orient="records")

    @task()
    def carregar(records):
        import pandas as pd
        from pipelines.current.load import load_current
        df = pd.DataFrame(records)
        return load_current(df=df)

    tempo_coleta = extrair()
    dados = transformar(tempo_coleta)
    carregar(dados)

dag_instance = weather_current_etl()