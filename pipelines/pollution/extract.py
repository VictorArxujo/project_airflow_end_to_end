import requests
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
import json
import os

logger = logging.getLogger(__name__)

def extract_pollution(city: str = "Londrina") -> str:
    api_key = os.getenv("API_KEY")

    # Busca coordenadas dinamicamente
    geo_url = "http://api.openweathermap.org/geo/1.0/direct"
    geo_params = {"q": f"{city},BR", "limit": 1, "appid": api_key}
    geo_response = requests.get(geo_url, params=geo_params)
    geo_response.raise_for_status()
    geo_data = geo_response.json()

    if not geo_data:
        raise ValueError(f"Cidade '{city}' não encontrada.")

    lat = geo_data[0]["lat"]
    lon = geo_data[0]["lon"]

    url = "https://api.openweathermap.org/data/2.5/air_pollution"
    params = {"lat": lat, "lon": lon, "appid": api_key}
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    data["_city_name"] = city
    data["_lat"] = lat
    data["_lon"] = lon
    agora = datetime.now(timezone(timedelta(hours=-3)))
    collected_at = agora.isoformat()
    data["_collected_at"] = collected_at

    city_slug = city.lower().replace(" ", "_")
    date_str = agora.strftime("%Y-%m-%d")
    time_str = agora.strftime("%Y%m%d_%H%M%S")
    path = Path(f"data/raw/pollution/{city_slug}/{date_str}")
    path.mkdir(parents=True, exist_ok=True)

    file_path = path / f"{city_slug}_{time_str}.json"
    with open(file_path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info(f"[pollution/extract] Salvo em {file_path}")
    return collected_at
