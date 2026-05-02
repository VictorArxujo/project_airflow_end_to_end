import requests
import logging
from datetime import datetime, timezone
from pathlib import Path
import json
import os

logger = logging.getLogger(__name__)

# Coordenadas de São Paulo
COORDS = {"São Paulo": {"lat": -23.5505, "lon": -46.6333}}

def extract_pollution(city: str = "São Paulo") -> str:
    api_key = os.getenv("API_KEY")
    lat = COORDS[city]["lat"]
    lon = COORDS[city]["lon"]

    url = "https://api.openweathermap.org/data/2.5/air_pollution"
    params = {"lat": lat, "lon": lon, "appid": api_key}

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    collected_at = datetime.now(timezone.utc).isoformat()

    city_slug = city.lower().replace(" ", "_")
    date_str = datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = Path(f"data/raw/pollution/{city_slug}/{date_str}")
    path.mkdir(parents=True, exist_ok=True)

    file_path = path / f"{city_slug}_{time_str}.json"
    data["_collected_at"] = collected_at
    with open(file_path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info(f"[pollution/extract] Salvo em {file_path}")
    return collected_at