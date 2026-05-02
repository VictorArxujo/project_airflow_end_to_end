import pandas as pd
import logging
from sqlalchemy import text
from core.db import get_engine

logger = logging.getLogger(__name__)

def load_forecast(df: pd.DataFrame) -> int:
    if df.empty:
        return 0

    engine = get_engine()

    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS weather_forecast (
                id SERIAL PRIMARY KEY,
                city_name TEXT,
                country TEXT,
                latitude FLOAT,
                longitude FLOAT,
                forecast_time TIMESTAMP,
                temperature FLOAT,
                feels_like FLOAT,
                humidity INT,
                pressure INT,
                weather_main TEXT,
                weather_desc TEXT,
                wind_speed FLOAT,
                pop FLOAT,
                collected_at TIMESTAMPTZ,
                UNIQUE (city_name, forecast_time, collected_at)
            )
        """))

    inserted = 0
    with engine.begin() as conn:
        for record in df.to_dict(orient="records"):
            result = conn.execute(text("""
                INSERT INTO weather_forecast
                    (city_name, country, latitude, longitude, forecast_time,
                     temperature, feels_like, humidity, pressure,
                     weather_main, weather_desc, wind_speed, pop, collected_at)
                VALUES
                    (:city_name, :country, :latitude, :longitude, :forecast_time,
                     :temperature, :feels_like, :humidity, :pressure,
                     :weather_main, :weather_desc, :wind_speed, :pop, :collected_at)
                ON CONFLICT (city_name, forecast_time, collected_at) DO NOTHING
            """), record)
            inserted += result.rowcount

    logger.info(f"[forecast/load] {inserted} linha(s) inserida(s)")
    return inserted