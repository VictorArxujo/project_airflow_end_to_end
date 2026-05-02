from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


API_BASE_URL = "https://api2.ploomes.com"
HEADERS = {
    "User-Key": os.getenv("KEY"),
    "Accept": "application/json"
}

ENTITIES = {
    "contacts": "/Contacts",
    "contacts_origins": "/Contacts@Origins",
    "deals": "/Deals",
    "deals_status": "/Deals@Status",
    "deals_stages": "/Deals@Stages",
    "deals_pipelines": "/Deals@Pipelines",
    "users": "/Users",
    "loss_reasons": "/Deals@LossReasons"
}

OUTPUT_PATH = "/tmp"


###Pegando os dados via api, usando paginacao pois temos limite de requisicao de 300 nas API
def fetch_paginated_data(endpoint, filename):
    url = API_BASE_URL + endpoint
    all_data = []

    while url:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Erro ao acessar {url}: {response.status_code} - {response.text}")
            break

        data = response.json()
        items = data.get('value', [])
        all_data.extend(items)
        url = data.get('@odata.nextLink', None)
        time.sleep(0.2)
    ##Transfromando to parquet para melhor otimizacao 
    df = pd.json_normalize(all_data)
    df.to_parquet(f"{OUTPUT_PATH}/{filename}.parquet", index=False)
    print(f"✅ Exportado: {filename}.parquet")

def fetch_non_paginated_data(endpoint, filename):
    url = API_BASE_URL + endpoint
    response = requests.get(url, headers=HEADERS)

    if response.status_code >= 200 and response.status_code < 300:
        data = response.json()
        if "value" in data:
            df = pd.DataFrame(data["value"])
            df.to_parquet(f"{OUTPUT_PATH}/{filename}.parquet", index=False)
            print(f"✅ Exportado: {filename}.parquet")
        else:
            print(f"⚠️ Nenhum dado encontrado em: {url}")
    else:
        print(f"❌ Erro ao acessar: {url} - {response.status_code}")


def create_task(task_id, endpoint, filename, paginated=True):
    if paginated:
        return PythonOperator(
            task_id=task_id,
            python_callable=fetch_paginated_data,
            op_args=[endpoint, filename],
        )
    else:
        return PythonOperator(
            task_id=task_id,
            python_callable=fetch_non_paginated_data,
            op_args=[endpoint, filename],
        )


def build_dag():
    default_args = {
        'owner': 'vanderson',
        'retries': 2,
        'retry_delay': timedelta(minutes=5),
        'start_date': datetime(2025, 4, 22,3)
    }

    with DAG(
        dag_id='get_data_from_api_ploomes',
        default_args=default_args,
        schedule_interval=None,
        catchup=False,
        tags=['ploomes', 'dados_api','chamando api'],
	doc_md= """
	### DAG: get_data_from_api_ploomes

	Esta DAG é responsável por **extrair dados do CRM Ploomes via API** e armazená-los como arquivos Parquet temporários na pasta `/tmp`.

	Ela executa 8 tarefas independentes, cada uma realizando um `GET` em um endpoint específico da API Ploomes:

	#### 🔹 Tarefas:
	- `fetch_contacts`: Extrai os contatos do CRM
	- `fetch_contacts_origins`: Extrai as origens dos contatos
	- `fetch_deals`: Extrai os negócios (deals)
	- `fetch_deals_status`: Extrai os status dos negócios
	- `fetch_deals_stages`: Extrai os estágios do funil
	- `fetch_deals_pipelines`: Extrai os funis (pipelines)
	- `fetch_users`: Extrai os usuários (responsáveis)
	- `fetch_loss_reasons`: Extrai os motivos de perda

	#### 📁 Armazenamento:
	Todos os dados extraídos são salvos como arquivos `.parquet` na pasta temporaria TMP para consumo posterior

	`ORQUESTRADA PELA DAG ORQUESTRADOR_INGESTAO_DATA_BRONZE`
"""
        
    ) as dag:

        tasks = [
            create_task('fetch_contacts', ENTITIES['contacts'], 'dados_contacts_ploomes'),
            create_task('fetch_contacts_origins', ENTITIES['contacts_origins'], 'dados_origins_ploomes', paginated=False),
            create_task('fetch_deals', ENTITIES['deals'], 'dados_deals_ploomes'),
            create_task('fetch_deals_status', ENTITIES['deals_status'], 'dados_status_deals_ploomes', paginated=False),
            create_task('fetch_deals_stages', ENTITIES['deals_stages'], 'dados_stages_ploomes', paginated=False),
            create_task('fetch_deals_pipelines', ENTITIES['deals_pipelines'], 'dados_pipelines_ploomes', paginated=False),
            create_task('fetch_users', ENTITIES['users'], 'dados_users_ploomes', paginated=False),
            create_task('fetch_loss_reasons', ENTITIES['loss_reasons'], 'dados_loss_reasons_ploomes', paginated=False)
        ]

        return dag


globals()['ingest_ploomes_bronze_dag'] = build_dag()
