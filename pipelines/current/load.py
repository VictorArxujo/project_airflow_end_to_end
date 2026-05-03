import logging
from sqlalchemy import text

from core.db import get_engine

logger = logging.getLogger(__name__)

COLUMNS = [
    "city_name", "country", "latitude", "longitude",
    "temperature", "feels_like", "temp_min", "temp_max",
    "pressure", "humidity", "visibility", "clouds",
    "wind_speed", "wind_deg", "wind_gust",
    "weather_main", "weather_desc",
    "sunrise", "sunset", "collected_at",
]

CREATE_TABLE = text("""
    CREATE TABLE IF NOT EXISTS weather_current (
        id           SERIAL PRIMARY KEY,
        city_name    TEXT,
        country      TEXT,
        latitude     FLOAT,
        longitude    FLOAT,
        temperature  FLOAT,
        feels_like   FLOAT,
        temp_min     FLOAT,
        temp_max     FLOAT,
        pressure     INT,
        humidity     INT,
        visibility   INT,
        clouds       INT,
        wind_speed   FLOAT,
        wind_deg     INT,
        wind_gust    FLOAT,
        weather_main TEXT,
        weather_desc TEXT,
        sunrise      TIMESTAMPTZ,
        sunset       TIMESTAMPTZ,
        collected_at TIMESTAMPTZ,
        inserted_at  TIMESTAMPTZ DEFAULT NOW(),
        UNIQUE (city_name, collected_at)
    )
""")


def load_current(records: list[dict]) -> int:
    if not records:
        logger.warning("[current/load] Lista vazia, nada para inserir.")
        return 0

    engine = get_engine()
    cols = ", ".join(COLUMNS)
    vals = ", ".join(f":{c}" for c in COLUMNS)

    sql = text(f"""
        INSERT INTO weather_current ({cols})
        VALUES ({vals})
        ON CONFLICT (city_name, collected_at) DO NOTHING
    """)

    with engine.begin() as conn:
        conn.execute(CREATE_TABLE)  # cria se não existir, ignora se já existir

    inserted = 0
    with engine.begin() as conn:
        for record in records:
            result = conn.execute(sql, record)
            inserted += result.rowcount

    logger.info(f"[current/load] {inserted} linha(s) inserida(s)")
    return inserted