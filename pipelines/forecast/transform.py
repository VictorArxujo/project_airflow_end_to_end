import logging
from datetime import datetime, timezone

from core.lake import load_raw

logger = logging.getLogger(__name__)


def transform_forecast(city: str, collected_at: str) -> list[dict]:
    """
    Retorna list[dict] — uma entrada por step de 3h (40 no total).
    """
    logger.info(f"[forecast/transform] Transformando dado de {city}")

    collected_at_dt = datetime.fromisoformat(collected_at)
    raw = load_raw(domain="forecast", city=city, collected_at=collected_at_dt)

    city_info = raw.get("city", {})
    records = []

    for item in raw.get("list", []):
        records.append({
            "city_name":    city_info.get("name"),
            "country":      city_info.get("country"),
            "latitude":     city_info.get("coord", {}).get("lat"),
            "longitude":    city_info.get("coord", {}).get("lon"),
            "forecast_time": item.get("dt_txt"),          # string "2026-05-03 15:00:00"
            "temperature":  item.get("main", {}).get("temp"),
            "feels_like":   item.get("main", {}).get("feels_like"),
            "temp_min":     item.get("main", {}).get("temp_min"),
            "temp_max":     item.get("main", {}).get("temp_max"),
            "pressure":     item.get("main", {}).get("pressure"),
            "humidity":     item.get("main", {}).get("humidity"),
            "clouds":       item.get("clouds", {}).get("all"),
            "wind_speed":   item.get("wind", {}).get("speed"),
            "wind_deg":     item.get("wind", {}).get("deg"),
            "wind_gust":    item.get("wind", {}).get("gust"),
            "weather_main": item.get("weather", [{}])[0].get("main"),
            "weather_desc": item.get("weather", [{}])[0].get("description"),
            "pop":          item.get("pop", 0),
            # rain só existe quando chove — .get() retorna None se ausente
            "rain_3h":      item.get("rain", {}).get("3h"),
            "visibility":   item.get("visibility"),
            "collected_at": collected_at,
        })

    logger.info(f"[forecast/transform] {len(records)} steps gerados para {city}")
    return records