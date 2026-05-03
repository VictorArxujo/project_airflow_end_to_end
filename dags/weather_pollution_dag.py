from airflow.decorators import dag, task
from datetime import datetime, timedelta

default_args = {
    "owner": "victor",
    "retries": 1,
    "retry_delay": timedelta(minutes=3),
}

@dag(
    dag_id="pipeline_poluicao",
    default_args=default_args,
    description="Pipeline de qualidade do ar via OpenWeather",
    schedule_interval="@hourly",
    start_date=datetime(2024, 5, 1),
    catchup=False,
    tags=["weather", "pollution"],
    params={"city": "Londrina"},
)
def weather_pollution_etl():

    @task()
    def extrair(**context) -> str:
        city = context["params"]["city"]
        from pipelines.pollution.extract import extract_pollution
        return extract_pollution(city=city)
        # retorna: str

    @task()
    def transformar(collected_at: str, **context) -> list:
        city = context["params"]["city"]
        from pipelines.pollution.transform import transform_pollution
        return transform_pollution(city=city, collected_at=collected_at)
        # retorna: list[dict]

    @task()
    def carregar(records: list) -> int:
        from pipelines.pollution.load import load_pollution
        return load_pollution(records=records)
        # retorna: int

    tempo_coleta = extrair()
    dados = transformar(tempo_coleta)
    carregar(dados)

dag_instance = weather_pollution_etl()