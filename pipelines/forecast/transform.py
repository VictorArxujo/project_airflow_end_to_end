import pandas as pd
import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

def transform_forecast(city: str = "Londrina", collected_at: str = None) -> pd.DataFrame:
    city_slug = city.lower().replace(" ", "_")
    date_str = datetime.now().strftime("%Y-%m-%d")
    path = sorted(Path(f"data/raw/forecast/{city_slug}/{date_str}").glob("*.json"))[-1]

    with open(path) as f:
        data = json.load(f)

    rows = []
    for item in data["list"]:
        rows.append({
            "city_name": data["city"]["name"],
            "country": data["city"]["country"],
            "latitude": data["city"]["coord"]["lat"],
            "longitude": data["city"]["coord"]["lon"],
            "forecast_time": item["dt_txt"],
            "temperature": item["main"]["temp"],
            "feels_like": item["main"]["feels_like"],
            "humidity": item["main"]["humidity"],
            "pressure": item["main"]["pressure"],
            "weather_main": item["weather"][0]["main"],
            "weather_desc": item["weather"][0]["description"],
            "wind_speed": item["wind"]["speed"],
            "pop": item.get("pop", 0),
            "collected_at": collected_at,
        })

    df = pd.DataFrame(rows)
    logger.info(f"[forecast/transform] {len(df)} linhas geradas")
    return df