from airflow.decorators import dag, task
from datetime import datetime, timedelta

default_args = {
    "owner": "victor",
    "retries": 1,
    "retry_delay": timedelta(minutes=3),
}

@dag(
    dag_id="pipeline_tempo_atual",
    default_args=default_args,
    description="Pipeline de extração do tempo atual via OpenWeather",
    schedule_interval="@hourly",
    start_date=datetime(2024, 5, 1),
    catchup=False,
    tags=["weather", "current"],
    params={"city": "Londrina"},
)
def weather_current_etl():

    @task()
    def extrair(**context) -> str:
        city = context["params"]["city"]
        from pipelines.current.extract import extract_current
        return extract_current(city=city)
        # retorna: str (ISO datetime)

    @task()
    def transformar(collected_at: str, **context) -> list:
        city = context["params"]["city"]
        from pipelines.current.transform import transform_current
        return transform_current(city=city, collected_at=collected_at)
        # recebe: str — retorna: list[dict]

    @task()
    def carregar(records: list) -> int:
        from pipelines.current.load import load_current
        return load_current(records=records)
        # recebe: list[dict] — retorna: int (linhas inseridas)

    tempo_coleta = extrair()
    dados = transformar(tempo_coleta)
    carregar(dados)

dag_instance = weather_current_etl()