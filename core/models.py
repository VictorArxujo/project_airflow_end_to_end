from sqlalchemy import Column, Integer, Float, String, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from core.db import Base


class WeatherCurrent(Base):
    """
    Dados do tempo atual — coletados a cada 1h por cidade.
    Unique constraint em (city_name + collected_at) evita duplicatas em reprocessamento.
    """
    __tablename__ = "weather_current"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    city_name     = Column(String(100), nullable=False)
    country       = Column(String(10))
    latitude      = Column(Float)
    longitude     = Column(Float)

    # temperatura
    temperature   = Column(Float)
    feels_like    = Column(Float)
    temp_min      = Column(Float)
    temp_max      = Column(Float)

    # atmosfera
    pressure      = Column(Integer)
    humidity      = Column(Integer)
    visibility    = Column(Integer)
    clouds        = Column(Integer)

    # vento
    wind_speed    = Column(Float)
    wind_deg      = Column(Integer)
    wind_gust     = Column(Float)

    # condição
    weather_main  = Column(String(50))
    weather_desc  = Column(String(100))

    # timestamps
    sunrise       = Column(DateTime(timezone=True))
    sunset        = Column(DateTime(timezone=True))
    collected_at  = Column(DateTime(timezone=True), nullable=False)
    inserted_at   = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("city_name", "collected_at", name="uq_current_city_time"),
    )


class WeatherForecast(Base):
    """
    Previsão horária para 5 dias (steps de 3h) — por cidade.
    """
    __tablename__ = "weather_forecast"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    city_name     = Column(String(100), nullable=False)
    country       = Column(String(10))

    forecast_at   = Column(DateTime(timezone=True), nullable=False)  # horário previsto
    collected_at  = Column(DateTime(timezone=True), nullable=False)  # quando foi extraído

    temperature   = Column(Float)
    feels_like    = Column(Float)
    temp_min      = Column(Float)
    temp_max      = Column(Float)
    pressure      = Column(Integer)
    humidity      = Column(Integer)
    clouds        = Column(Integer)
    wind_speed    = Column(Float)
    wind_deg      = Column(Integer)
    wind_gust     = Column(Float)
    visibility    = Column(Integer)
    pop           = Column(Float)   # probability of precipitation (0–1)
    rain_3h       = Column(Float)   # mm de chuva nas últimas 3h (pode ser null)
    weather_main  = Column(String(50))
    weather_desc  = Column(String(100))

    inserted_at   = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("city_name", "forecast_at", "collected_at", name="uq_forecast_city_time"),
    )


class AirPollution(Base):
    """
    Qualidade do ar (AQI + componentes) — por cidade, a cada 1h.
    """
    __tablename__ = "air_pollution"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    city_name     = Column(String(100), nullable=False)
    latitude      = Column(Float)
    longitude     = Column(Float)

    aqi           = Column(Integer)   # 1=Boa, 2=Razoável, 3=Moderada, 4=Ruim, 5=Péssima

    # componentes em µg/m³
    co            = Column(Float)   # monóxido de carbono
    no            = Column(Float)   # monóxido de nitrogênio
    no2           = Column(Float)   # dióxido de nitrogênio
    o3            = Column(Float)   # ozônio
    so2           = Column(Float)   # dióxido de enxofre
    pm2_5         = Column(Float)   # partículas finas
    pm10          = Column(Float)   # partículas grossas
    nh3           = Column(Float)   # amônia

    collected_at  = Column(DateTime(timezone=True), nullable=False)
    inserted_at   = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("city_name", "collected_at", name="uq_pollution_city_time"),
    )