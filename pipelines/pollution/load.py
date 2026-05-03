import logging
from sqlalchemy import text

from core.db import get_engine

logger = logging.getLogger(__name__)

COLUMNS = [
    "city_name", "latitude", "longitude",
    "aqi", "aqi_label",
    "co", "no", "no2", "o3", "so2", "pm2_5", "pm10", "nh3",
    "collected_at",
]

CREATE_TABLE = text("""
    CREATE TABLE IF NOT EXISTS weather_pollution (
        id           SERIAL PRIMARY KEY,
        city_name    TEXT,
        latitude     FLOAT,
        longitude    FLOAT,
        aqi          INT,
        aqi_label    TEXT,
        co           FLOAT,
        no           FLOAT,
        no2          FLOAT,
        o3           FLOAT,
        so2          FLOAT,
        pm2_5        FLOAT,
        pm10         FLOAT,
        nh3          FLOAT,
        collected_at TIMESTAMPTZ,
        inserted_at  TIMESTAMPTZ DEFAULT NOW(),
        UNIQUE (city_name, collected_at)
    )
""")


def load_pollution(records: list[dict]) -> int:
    if not records:
        logger.warning("[pollution/load] Lista vazia.")
        return 0

    engine = get_engine()
    cols = ", ".join(COLUMNS)
    vals = ", ".join(f":{c}" for c in COLUMNS)

    sql = text(f"""
        INSERT INTO weather_pollution ({cols})
        VALUES ({vals})
        ON CONFLICT (city_name, collected_at) DO NOTHING
    """)

    with engine.begin() as conn:
        conn.execute(CREATE_TABLE)

    inserted = 0
    with engine.begin() as conn:
        for record in records:
            result = conn.execute(sql, record)
            inserted += result.rowcount

    logger.info(f"[pollution/load] {inserted} linha(s) inserida(s)")
    return inserted