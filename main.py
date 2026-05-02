from pipelines.current.extract import extract_current
from pipelines.current.transform import transform_current
from pipelines.current.load import load_current
import logging
from pathlib import Path
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

env_path = Path(__file__).resolve().parent / 'config' / '.env'
load_dotenv(env_path)

def pipeline():
    try:
        logging.info("ETAPA 1: EXTRACT")
        collected_at = extract_current(city="São Paulo")

        logging.info("ETAPA 2: TRANSFORM")
        df = transform_current(city="São Paulo", collected_at=collected_at)

        logging.info("ETAPA 3: LOAD")
        load_current(df=df)

        print("\n" + "="*60)
        print("✅ Pipeline concluído com sucesso!")
        print("="*60)

    except Exception as e:
        logging.error(f"❌ ERRO no Pipeline: {e}")
        import traceback
        traceback.print_exc()

pipeline()