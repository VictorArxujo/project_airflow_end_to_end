import logging
from sqlalchemy import text

from core.db import get_engine

logger = logging.getLogger(__name__)

COLUMNS = [
    "city_name", "country", "latitude", "longitude",
    "forecast_time", "temperature", "feels_like", "temp_min", "temp_max",
    "pressure", "humidity", "clouds", "wind_speed", "wind_deg", "wind_gust",
    "weather_main", "weather_desc", "pop", "rain_3h", "visibility", "collected_at",
]

CREATE_TABLE = text("""
    CREATE TABLE IF NOT EXISTS weather_forecast (
        id            SERIAL PRIMARY KEY,
        city_name     TEXT,
        country       TEXT,
        latitude      FLOAT,
        longitude     FLOAT,
        forecast_time TIMESTAMP,
        temperature   FLOAT,
        feels_like    FLOAT,
        temp_min      FLOAT,
        temp_max      FLOAT,
        pressure      INT,
        humidity      INT,
        clouds        INT,
        wind_speed    FLOAT,
        wind_deg      INT,
        wind_gust     FLOAT,
        weather_main  TEXT,
        weather_desc  TEXT,
        pop           FLOAT,
        rain_3h       FLOAT,
        visibility    INT,
        collected_at  TIMESTAMPTZ,
        inserted_at   TIMESTAMPTZ DEFAULT NOW(),
        UNIQUE (city_name, forecast_time, collected_at)
    )
""")


def load_forecast(records: list[dict]) -> int:
    if not records:
        logger.warning("[forecast/load] Lista vazia.")
        return 0

    engine = get_engine()
    cols = ", ".join(COLUMNS)
    vals = ", ".join(f":{c}" for c in COLUMNS)

    sql = text(f"""
        INSERT INTO weather_forecast ({cols})
        VALUES ({vals})
        ON CONFLICT (city_name, forecast_time, collected_at) DO NOTHING
    """)

    with engine.begin() as conn:
        conn.execute(CREATE_TABLE)

    inserted = 0
    with engine.begin() as conn:
        for record in records:
            result = conn.execute(sql, record)
            inserted += result.rowcount

    logger.info(f"[forecast/load] {inserted} linha(s) inserida(s)")
    return inserted