import pandas as pd
import logging
from sqlalchemy import text
from core.db import get_engine

logger = logging.getLogger(__name__)

def load_pollution(df: pd.DataFrame) -> int:
    if df.empty:
        return 0

    engine = get_engine()

    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS weather_pollution (
                id SERIAL PRIMARY KEY,
                city_name TEXT,
                latitude FLOAT,
                longitude FLOAT,
                aqi INT,
                aqi_label TEXT,
                co FLOAT,
                no FLOAT,
                no2 FLOAT,
                o3 FLOAT,
                so2 FLOAT,
                pm2_5 FLOAT,
                pm10 FLOAT,
                nh3 FLOAT,
                collected_at TIMESTAMPTZ,
                UNIQUE (city_name, collected_at)
            )
        """))

    inserted = 0
    with engine.begin() as conn:
        for record in df.to_dict(orient="records"):
            result = conn.execute(text("""
                INSERT INTO weather_pollution
                    (city_name, latitude, longitude, aqi, aqi_label,
                     co, no, no2, o3, so2, pm2_5, pm10, nh3, collected_at)
                VALUES
                    (:city_name, :latitude, :longitude, :aqi, :aqi_label,
                     :co, :no, :no2, :o3, :so2, :pm2_5, :pm10, :nh3, :collected_at)
                ON CONFLICT (city_name, collected_at) DO NOTHING
            """), record)
            inserted += result.rowcount

    logger.info(f"[pollution/load] {inserted} linha(s) inserida(s)")
    return inserted