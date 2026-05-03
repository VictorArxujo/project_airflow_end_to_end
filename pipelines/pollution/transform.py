import logging
from datetime import datetime

from core.lake import load_raw

logger = logging.getLogger(__name__)

AQI_LABEL = {1: "Boa", 2: "Razoável", 3: "Moderada", 4: "Ruim", 5: "Muito Ruim"}


def transform_pollution(city: str, collected_at: str) -> list[dict]:
    """
    Retorna list[dict] com uma linha — pollution tem sempre um item na lista.
    """
    logger.info(f"[pollution/transform] Transformando dado de {city}")

    collected_at_dt = datetime.fromisoformat(collected_at)
    raw = load_raw(domain="pollution", city=city, collected_at=collected_at_dt)

    item = raw.get("list", [{}])[0]
    aqi = item.get("main", {}).get("aqi")
    components = item.get("components", {})

    record = {
        "city_name":  raw.get("_city_name", city),
        "latitude":   raw.get("_lat"),
        "longitude":  raw.get("_lon"),
        "aqi":        aqi,
        "aqi_label":  AQI_LABEL.get(aqi, "Desconhecido"),
        "co":         components.get("co"),
        "no":         components.get("no"),
        "no2":        components.get("no2"),
        "o3":         components.get("o3"),
        "so2":        components.get("so2"),
        "pm2_5":      components.get("pm2_5"),
        "pm10":       components.get("pm10"),
        "nh3":        components.get("nh3"),
        "collected_at": collected_at,
    }

    logger.info(f"[pollution/transform] Concluído para {city}")
    return [record]