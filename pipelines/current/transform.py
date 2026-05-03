import logging
from datetime import datetime, timezone

from core.lake import load_raw

logger = logging.getLogger(__name__)


def transform_current(city: str, collected_at: str) -> list[dict]:
    """
    Carrega o JSON bruto, normaliza e retorna list[dict] — serializável pelo XCom.

    Recebe:
        collected_at: string ISO (vem do extract via XCom)
    Retorna:
        list[dict] — JSON-safe, passa pelo XCom sem problema
    """
    logger.info(f"[current/transform] Transformando dado de {city}")

    # Converte string ISO de volta para datetime para buscar o arquivo no lake
    collected_at_dt = datetime.fromisoformat(collected_at)

    raw = load_raw(domain="current", city=city, collected_at=collected_at_dt)

    # weather é sempre uma lista — pega o primeiro elemento
    weather_info = raw.get("weather", [{}])[0]

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
        # Timestamps: Unix → string ISO (nunca datetime — não é JSON-safe)
        "sunrise":      _unix_to_iso(raw.get("sys", {}).get("sunrise")),
        "sunset":       _unix_to_iso(raw.get("sys", {}).get("sunset")),
        "collected_at": collected_at,  # já é string, repassa direto
    }

    logger.info(f"[current/transform] Concluído para {city}")
    return [record]  # sempre list[dict] — mesmo que seja um registro só


def _unix_to_iso(unix_ts: int | None) -> str | None:
    """Unix timestamp → string ISO UTC. None → None."""
    if unix_ts is None:
        return None
    return datetime.fromtimestamp(unix_ts, tz=timezone.utc).isoformat()