import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv(Path(__file__).resolve().parent / 'config' / '.env')

engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM weather_current ORDER BY collected_at DESC"))
    df = pd.DataFrame(result.fetchall(), columns=result.keys())

print(f"\nTotal de registros: {len(df)}")
print(df[["city_name", "temperature", "feels_like", "humidity", "weather_desc", "collected_at"]])
