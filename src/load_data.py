from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
import pandas as pd
import os
import logging
from dotenv import load_dotenv
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

env_path = Path(__file__).parent.parent / 'config' / '.env'
load_dotenv(env_path)

user = os.getenv('DB_USER')
database = os.getenv('DB_NAME')
password = os.getenv('DB_PASSWORD')


def get_engine():
    # Vamos forçar a string diretamente aqui dentro para evitar problemas de cache de variáveis
    host_certo = 'postgres_etl'
    url_conexao = f"postgresql+psycopg2://{user}:{quote_plus(password)}@{host_certo}:5432/{database}"
    logging.info(f"→ Conectando em: {url_conexao}") # Vai imprimir a string inteira no log (cuidado pra não vazar a senha se for postar print!)
    
    return create_engine(url_conexao)
    
engine = get_engine()

def load_data(table_name:str, df):
    print('entrei aqui')
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists='append',
        index=False
    )
    
    logging.info(f"✅ Dados carregados com sucesso!\n") 
    
    df_check = pd.read_sql(f'SELECT * FROM {table_name}', con=engine)
    logging.info(f"Total de registros na tabela: {len(df_check)}\n")