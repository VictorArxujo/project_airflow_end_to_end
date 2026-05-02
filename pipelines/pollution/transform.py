import pandas as pd
import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

AQI_LABEL = {1: "Boa", 2: "Razoável", 3: "Moderada", 4: "Ruim", 5: "Muito Ruim"}

def transform_pollution(city: str = "Londrina", collected_at: str = None) -> pd.DataFrame:
    city_slug = city.lower().replace(" ", "_")
    date_str = datetime.now().strftime("%Y-%m-%d")
    path = sorted(Path(f"data/raw/pollution/{city_slug}/{date_str}").glob("*.json"))[-1]

    with open(path) as f:
        data = json.load(f)

    item = data["list"][0]
    aqi = item["main"]["aqi"]
    components = item["components"]

    df = pd.DataFrame([{
        "city_name": data.get("_city_name", city),
        "latitude": data.get("_lat"),
        "longitude": data.get("_lon"),
        "aqi": aqi,
        "aqi_label": AQI_LABEL.get(aqi, "Desconhecido"),
        "co": components.get("co"),
        "no": components.get("no"),
        "no2": components.get("no2"),
        "o3": components.get("o3"),
        "so2": components.get("so2"),
        "pm2_5": components.get("pm2_5"),
        "pm10": components.get("pm10"),
        "nh3": components.get("nh3"),
        "collected_at": collected_at,
    }])

    logger.info(f"[pollution/transform] {len(df)} linha(s) gerada(s)")
    return df
