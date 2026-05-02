import logging
from datetime import datetime, timezone

from core.lake import load_raw

logger = logging.getLogger(__name__)


def transform_current(city: str, collected_at: datetime) -> list:
    """
    Carrega o JSON bruto do data lake, limpa e normaliza os dados,
    retornando uma lista de dicionários pronta para inserção no banco e XCom.

    Args:
        city:         nome da cidade
        collected_at: datetime da coleta (vem do extract)

    Returns:
        Lista com um dicionário contendo as colunas mapeadas para WeatherCurrent
    """
    logger.info(f"[current/transform] Transformando dado de {city}")

    # 1. carrega o JSON bruto que o extract salvou
    raw = load_raw(domain="current", city=city, collected_at=collected_at)

    # 2. o campo weather é uma lista — sempre pegamos o primeiro elemento
    weather_info = raw.get("weather", [{}])[0]

    # 3. monta o dicionário já com os campos renomeados e limpos
    record = {
        "city_name":    raw.get("name"),
        "country":      raw.get("sys", {}).get("country"),
        "latitude":     raw.get("coord", {}).get("lat"),
        "longitude":    raw.get("coord", {}).get("lon"),
        "temperature":  raw.get("main", {}).get("temp"),
        "feels_like":   raw.get("main", {}).get("feels_like"),
        "temp_min":     raw.get("main", {}).get("temp_min"),
        "temp_max":     raw.get("main", {}).get("temp_max"),
        "pressure":     raw.get("main", {}).get("pressure"),
        "humidity":     raw.get("main", {}).get("humidity"),
        "visibility":   raw.get("visibility"),
        "clouds":       raw.get("clouds", {}).get("all"),
        "wind_speed":   raw.get("wind", {}).get("speed"),
        "wind_deg":     raw.get("wind", {}).get("deg"),
        "wind_gust":    raw.get("wind", {}).get("gust"),
        "weather_main": weather_info.get("main"),
        "weather_desc": weather_info.get("description"),
        
        # Converte para strings ISO para não dar erro de JSON no Airflow
        "sunrise":      _unix_to_iso(raw.get("sys", {}).get("sunrise")),
        "sunset":       _unix_to_iso(raw.get("sys", {}).get("sunset")),
        "collected_at": collected_at.isoformat() if isinstance(collected_at, datetime) else collected_at,
    }

    logger.info(f"[current/transform] Concluído — 1 linha pronta para {city}")
    
    # Retorna uma LISTA com o dicionário dentro
    return [record]


def _unix_to_iso(unix_ts: int | None) -> str | None:
    """Converte timestamp Unix para string ISO segura para JSON/XCom."""
    if unix_ts is None:
        return None
    return datetime.fromtimestamp(unix_ts, tz=timezone.utc).isoformat()