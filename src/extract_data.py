import requests
import json
from pathlib import Path
import logging 
import os
import dotenv
dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') 
api_key = os.getenv('config/API_KEY')

lat = -23.5505
lon = -46.6333



def extract_weather() -> list:
    url= f'https://api.openweathermap.org/data/2.5/weather?q=Sao Paulo,BR&units=metric&appid=c25c76bb18536cb73ab8282d38e5a3ab'

    response = requests.get(url)
    data = response.json()
   
    if response.status_code != 200:
        logging.error('Falha na requisição, status code: %s, response: %s', response.status_code, data)
        return []
    
    if not data:
        logging.warning('Nenhum dado encontrado')
        return []


    output_path = "data/weather_data.json"
    output_dir = Path(output_path).parent.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w") as f:
        json.dump(data, f, indent=4)
        logging.info(f'Dados salvos em {output_path}')

    return data
