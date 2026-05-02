import pandas as pd
from pathlib import Path
import json

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

path_name = Path(__file__).parent.parent / 'data' / 'weather_data.json'
columns_names_to_drop = ['weather', 'weather_icon','sys.type']
columns_names_to_rename = {
        "base": "base",
        "visibility": "visibility",
        "dt": "datetime",
        "timezone": "timezone",
        "id": "city_id", 
        "name": "city_name",
        "cod": "code",
        "coord.lon": "longitude",
        "coord.lat": "latitude",
        "main.temp": "temperature",
        "main.feels_like": "feels_like",
        "main.temp_min": "temp_min",
        "main.temp_max": "temp_max",
        "main.pressure": "pressure",
        "main.humidity": "humidity",
        "main.sea_level": "sea_level",
        "main.grnd_level": "grnd_level",
        "wind.speed": "wind_speed",
        "wind.deg": "wind_deg",
        "wind.gust": "wind_gust",
        "clouds.all": "clouds", 
        "sys.type": "sys_type",                 
        "sys.id": "sys_id",                
        "sys.country": "country",                
        "sys.sunrise": "sunrise",                
        "sys.sunset": "sunset",
        # weather_id, weather_main, weather_description 
    }

def create_dataframe(path_name:str) -> pd.DataFrame:

    logging.info(f'Lendo dados do arquivo {path_name}')
    path = Path(path_name)
    
    if not path.exists():
        raise FileNotFoundError(f'Arquivo {path_name} não encontrado')
    
    with open(path) as f:
        data = json.load(f)

    df = pd.json_normalize(data)
    logging.info(f'Dataframe criado com {len(df)} linhas e {len(df.columns)} colunas')
    
    return df

def normalize_weather_columns(df: pd.DataFrame) -> pd.DataFrame:

        df_weather = pd.json_normalize(df['weather'].apply(lambda x: x[0]))


        df_weather = df_weather.rename(columns={
            'id': 'weather_id',
            'main': 'weather_main',
            'description': 'weather_description',
            'icon': 'weather_icon'
        })  

        df = pd.concat([df, df_weather], axis=1)
        logging.info(f'Colunas normalizadas: {df_weather.columns.tolist()}')
        return df

def drop_columns(df: pd.DataFrame, columns_to_drop: list[str]) -> pd.DataFrame:

    logging.info(f'Colunas a serem removidas: {columns_to_drop}')
    df = df.drop(columns=columns_to_drop)
    logging.info(f'Colunas removidas: {columns_to_drop}')
    return df

def rename_columns(df: pd.DataFrame, columns_to_rename: dict[str, str]) -> pd.DataFrame:
    logging.info(f'Colunas a serem renomeadas: {columns_to_rename}')
    df = df.rename(columns=columns_to_rename)
    logging.info(f'Colunas renomeadas: {df.columns.tolist()}')
    return df

def normalize_datetime_columns(df: pd.DataFrame, columns_to_normalize: list[str]) -> pd.DataFrame:
    logging.info(f'Colunas a serem normalizadas para datetime: {columns_to_normalize}')
    for name in columns_to_normalize:
        df[name] = pd.to_datetime(df[name], unit='s', utc=True).dt.tz_convert('America/Sao_Paulo')
        logging.info(f'Coluna {name} normalizada para datetime')          
   
    return df
    
def data_transformations():
    print ('iniciando transformações de dados')
    df = create_dataframe(path_name)
    df = normalize_weather_columns(df)
    df = drop_columns(df, columns_names_to_drop)
    df = rename_columns(df, columns_names_to_rename)
    df = normalize_datetime_columns(df, ['datetime', 'sunrise', 'sunset'])
    logging.info('Transformações de dados concluídas')
    return df
