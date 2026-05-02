import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from pathlib import Path
import os

env_path = Path(__file__).resolve().parent / 'config' / '.env'
load_dotenv(env_path)

engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# ✅ usa .connect() para passar ao pandas
with engine.connect() as conn:
    df = pd.read_sql("SELECT * FROM weather_current ORDER BY collected_at DESC", conn)

print(f"\nTotal de registros: {len(df)}")
print(df[["city_name", "temperature", "feels_like", "humidity", "weather_desc", "collected_at"]])