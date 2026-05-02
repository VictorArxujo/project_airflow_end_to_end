from src.extract_data import extract_weather
from src.load_data import load_data
from src.transform_data import data_transformations
import os
from pathlib import Path
from dotenv import load_dotenv
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
env_path = Path(__file__).resolve().parent.parent / 'config' / '.env'
load_dotenv(env_path)
api_key = os.getenv('API_KEY')

table_name = 'sp_weather'

def pipeline():
    try:
        logging.info("ETAPA 1: EXTRACT")
        extract_weather()
    
        logging.info("ETAPA 2: TRANSFORM")
        df = data_transformations()
    
        logging.info("ETAPA 3: LOAD")
        load_data(table_name, df)
    
        print("\n" + "="*60)
        print("✅ Pipeline concluído com sucesso!")
        print("="*60)
    
    except Exception as e:
        logging.error(f"❌ ERRO no Pipeline: {e}")
        import traceback
        traceback.print_exc()


pipeline()