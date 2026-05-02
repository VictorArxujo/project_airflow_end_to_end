import requests
import logging
from datetime import datetime, timezone
from pathlib import Path
import json
import os

logger = logging.getLogger(__name__)

def extract_forecast(city: str = "São Paulo") -> str:
    api_key = os.getenv("API_KEY")
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"q": f"{city},BR", "units": "metric", "lang": "pt_br", "appid": api_key}

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    collected_at = datetime.now(timezone.utc).isoformat()

    city_slug = city.lower().replace(" ", "_")
    date_str = datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = Path(f"data/raw/forecast/{city_slug}/{date_str}")
    path.mkdir(parents=True, exist_ok=True)

    file_path = path / f"{city_slug}_{time_str}.json"
    data["_collected_at"] = collected_at
    with open(file_path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info(f"[forecast/extract] Salvo em {file_path}")
    return collected_at