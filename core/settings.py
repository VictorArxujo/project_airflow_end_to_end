from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path
from typing import List

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / "config" / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- OpenWeather ---
    api_key: str = Field(..., alias="API_KEY")
    openweather_base_url: str = "https://api.openweathermap.org"

    # Cidades monitoradas (separadas por vírgula no .env)
    # Ex: CITIES=São Paulo,Rio de Janeiro,Curitiba
    cities: List[str] = Field(
        default=["São Paulo"],
        alias="CITIES",
    )

    # --- Banco de dados ETL ---
    db_user: str = Field(default="victor", alias="DB_USER")
    db_password: str = Field(default="victor", alias="DB_PASSWORD")
    db_host: str = Field(default="postgres_etl", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_name: str = Field(default="projeto_etl", alias="DB_NAME")

    @property
    def database_url(self) -> str:
        from urllib.parse import quote_plus
        return (
            f"postgresql+psycopg2://{self.db_user}:"
            f"{quote_plus(self.db_password)}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )

    # --- Data lake local ---
    data_dir: Path = Field(default=BASE_DIR / "data")

    @property
    def raw_dir(self) -> Path:
        return self.data_dir / "raw"

    @property
    def processed_dir(self) -> Path:
        return self.data_dir / "processed"


# instância global — importar de qualquer lugar com:
# from core.settings import settings
settings = Settings()