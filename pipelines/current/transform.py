import pandas as pd
import logging
from datetime import datetime, timezone

from core.lake import load_raw

logger = logging.getLogger(__name__)


def transform_current(city: str, collected_at: datetime) -> pd.DataFrame:
    """
    Carrega o JSON bruto do data lake, limpa e normaliza os dados,
    retornando um DataFrame com uma linha pronta para inserção no banco.

    Args:
        city:         nome da cidade
        collected_at: datetime da coleta (vem do extract)

    Returns:
        DataFrame com uma linha e colunas mapeadas para WeatherCurrent
    """
    logger.info(f"[current/transform] Transformando dado de {city}")

    # 1. carrega o JSON bruto que o extract salvou
    raw = load_raw(domain="current", city=city, collected_at=collected_at)

    # 2. o campo weather é uma lista — sempre pegamos o primeiro elemento
    weather_info = raw.get("weather", [{}])[0]

    # 3. monta o dicionário já com os campos renomeados e limpos
    record = {
        # identificação
        "city_name":    raw.get("name"),
        "country":      raw.get("sys", {}).get("country"),
        "latitude":     raw.get("coord", {}).get("lat"),
        "longitude":    raw.get("coord", {}).get("lon"),

        # temperatura
        "temperature":  raw.get("main", {}).get("temp"),
        "feels_like":   raw.get("main", {}).get("feels_like"),
        "temp_min":     raw.get("main", {}).get("temp_min"),
        "temp_max":     raw.get("main", {}).get("temp_max"),

        # atmosfera
        "pressure":     raw.get("main", {}).get("pressure"),
        "humidity":     raw.get("main", {}).get("humidity"),
        "visibility":   raw.get("visibility"),
        "clouds":       raw.get("clouds", {}).get("all"),

        # vento — gust pode não existir, .get() retorna None sem quebrar
        "wind_speed":   raw.get("wind", {}).get("speed"),
        "wind_deg":     raw.get("wind", {}).get("deg"),
        "wind_gust":    raw.get("wind", {}).get("gust"),

        # condição do tempo
        "weather_main": weather_info.get("main"),
        "weather_desc": weather_info.get("description"),

        # timestamps — dt é Unix timestamp, convertemos para datetime com timezone
        "sunrise":      _unix_to_datetime(raw.get("sys", {}).get("sunrise")),
        "sunset":       _unix_to_datetime(raw.get("sys", {}).get("sunset")),
        "collected_at": collected_at,
    }

    df = pd.DataFrame([record])

    logger.info(f"[current/transform] Concluído — {len(df)} linha(s) para {city}")
    return df


def _unix_to_datetime(unix_ts: int | None) -> datetime | None:
    """Converte timestamp Unix (inteiro) para datetime com timezone UTC."""
    if unix_ts is None:
        return None
    return datetime.fromtimestamp(unix_ts, tz=timezone.utc)