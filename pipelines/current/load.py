import logging
from sqlalchemy import text
from core.db import get_engine

logger = logging.getLogger(__name__)


def load_current(records: list) -> int:
    if not records:
        logger.warning("[current/load] Lista vazia, nada para inserir.")
        return 0

    engine = get_engine()

    # Cria a tabela se não existir
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS weather_current (
                id SERIAL PRIMARY KEY,
                city_name TEXT,
                country TEXT,
                latitude FLOAT,
                longitude FLOAT,
                temperature FLOAT,
                feels_like FLOAT,
                humidity INT,
                pressure INT,
                weather_main TEXT,
                weather_desc TEXT,
                wind_speed FLOAT,
                sunrise TIMESTAMPTZ,
                sunset TIMESTAMPTZ,
                collected_at TIMESTAMPTZ,
                UNIQUE (city_name, collected_at)
            )
        """))

    inserted = 0

    # Insere iterando direto sobre a lista que veio do Transform
    with engine.begin() as conn:
        for record in records:
            result = conn.execute(text("""
                INSERT INTO weather_current 
                    (city_name, country, latitude, longitude, temperature,
                     feels_like, humidity, pressure, weather_main, 
                     weather_desc, wind_speed, sunrise, sunset, collected_at)
                VALUES 
                    (:city_name, :country, :latitude, :longitude, :temperature,
                     :feels_like, :humidity, :pressure, :weather_main,
                     :weather_desc, :wind_speed, :sunrise, :sunset, :collected_at)
                ON CONFLICT (city_name, collected_at) DO NOTHING
            """), record)
            inserted += result.rowcount

    logger.info(f"[current/load] {inserted} linha(s) inserida(s) na weather_current")
    return inserted