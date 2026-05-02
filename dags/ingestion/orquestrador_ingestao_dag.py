from airflow import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime, timedelta

def build_dag():
    default_args = {
        'owner': 'vanderson',
        'retries': 4,
        'retry_delay': timedelta(minutes=2),
        'start_date': datetime(2025, 4, 23, 2),
    }

    with DAG(
        dag_id='orquestrador_ingestao_data_bronze',
        default_args=default_args,
        schedule_interval=None,  # Execução manual ou por outro processo
        catchup=False,
        tags=['orquestrador', 'ploomes', 'bronze', 'etl'],
	doc_md = 
	"""
	### DAG: orquestrador_ingestao_dag

	Esta DAG atua como **orquestradora do pipeline de ingestão de dados do CRM Ploomes**, disparando em sequência as seguintes DAGs:

	1. `get_data_from_api_ploomes` → realiza a extração dos dados da API do Ploomes e salva como `.parquet`.
	2. `send_data_to_bronze_db` → carrega os dados `.parquet` extraídos para o schema `bronze` do banco de dados `cmsolar`.

	#### ⚙️ Operadores utilizados:
	- Utiliza `TriggerDagRunOperator` para acionar a execução de DAGs externas de forma encadeada.

	#### 🔄 Fluxo orquestrado:
	orquestrador_ingestao_dag ├──> get_data_from_api_ploomes └──> send_data_to_bronze_db
	
	#### 📌 Ordem garantida:
	- Garante que a DAG de extração (`get_data_from_api_ploomes`) **seja executada antes da DAG de carga** (`send_data_to_bronze_db`), assegurando que os dados salvos no banco estejam atualizados com as últimas informações da API.
	
	`DAG ORQUESTRADA PELA DAG ORQUESTRADOR_PIPELINE_COMPLETO `
	"""
    ) as dag:

        trigger_ingest_bronze = TriggerDagRunOperator(
            task_id='get_api_data_from_crm',
            trigger_dag_id='get_data_from_api_ploomes',
            wait_for_completion=True,
            poke_interval=60,  # verifica a cada 30 segundos
            reset_dag_run=True,
            execution_timeout=timedelta(minutes=10),  # ⏱ tempo limite de execução
        )

        trigger_bronze_to_db = TriggerDagRunOperator(
            task_id='post_data_to_db_bronze',
            trigger_dag_id='post_data_to_bronze_db',
            wait_for_completion=True,
            poke_interval=60,
            reset_dag_run=True,
            execution_timeout=timedelta(minutes=10),  # ⏱ tempo limite de execução
        )

        trigger_ingest_bronze >> trigger_bronze_to_db

        return dag

globals()['orquestrador_ingestao_data_bronze'] = build_dag()
