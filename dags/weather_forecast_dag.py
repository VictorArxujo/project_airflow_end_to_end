from airflow.decorators import dag, task
from datetime import datetime, timedelta

default_args = {
    'owner': 'victor',
    'retries': 1,
    'retry_delay': timedelta(minutes=3),
}

@dag(
    dag_id='pipeline_previsao',
    default_args=default_args,
    description='Pipeline de previsão do tempo via OpenWeather',
    schedule_interval='@hourly',
    start_date=datetime(2024, 5, 1),
    catchup=False,
    tags=['weather', 'forecast'],
    params={"city": "Londrina"},  # ✅ default aqui
)
def weather_forecast_etl():

    @task()
    def extrair():
        from pipelines.forecast.extract import extract_forecast
        return extract_forecast(city="Londrina")  # retorna collected_at (string/datetime)

    @task()
    def transformar(collected_at):
        from pipelines.forecast.transform import transform_forecast
        df = transform_forecast(city="Londrina", collected_at=collected_at)
        return df.to_dict(orient="records")  # ✅ converte para lista de dicts

    @task()
    def carregar(records):
        import pandas as pd
        from pipelines.forecast.load import load_forecast
        df = pd.DataFrame(records)  # ✅ reconstrói o DataFrame
        return load_forecast(df=df)

    tempo_coleta = extrair()
    dados = transformar(tempo_coleta)
    carregar(dados)

dag_instance = weather_forecast_etl()