from airflow.decorators import dag, task
from datetime import datetime, timedelta

default_args = {
    "owner": "victor",
    "retries": 1,
    "retry_delay": timedelta(minutes=3),
}

@dag(
    dag_id="pipeline_previsao",
    default_args=default_args,
    description="Pipeline de previsão do tempo via OpenWeather",
    schedule_interval="@hourly",
    start_date=datetime(2024, 5, 1),
    catchup=False,
    tags=["weather", "forecast"],
    params={"city": "Londrina"},
)
def weather_forecast_etl():

    @task()
    def extrair(**context) -> str:
        city = context["params"]["city"]
        from pipelines.forecast.extract import extract_forecast
        return extract_forecast(city=city)
        # retorna: str

    @task()
    def transformar(collected_at: str, **context) -> list:
        city = context["params"]["city"]
        from pipelines.forecast.transform import transform_forecast
        return transform_forecast(city=city, collected_at=collected_at)
        # retorna: list[dict]

    @task()
    def carregar(records: list) -> int:
        from pipelines.forecast.load import load_forecast
        return load_forecast(records=records)
        # retorna: int

    tempo_coleta = extrair()
    dados = transformar(tempo_coleta)
    carregar(dados)

dag_instance = weather_forecast_etl()