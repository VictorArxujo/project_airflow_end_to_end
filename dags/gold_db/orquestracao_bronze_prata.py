from airflow import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime, timedelta


default_args= {
	'owner':'vanderson',
	'retries':5,
	'retry_delay':timedelta(minutes=5)


}


with DAG(
    default_args=default_args,
    dag_id="orquestrador_pipeline_completo",
    start_date=datetime(2025, 4, 30),
    schedule_interval='0 0 * * *',
    catchup=False,
    tags=["pipeline", "bronze", "prata"],
    description="Orquestra pipeline completo do Bronze ao Prata",
    doc_md= 
    """
Esta DAG executa a **orquestração completa do pipeline de dados**, conectando as etapas de ingestão da camada bronze até a carga final na camada prata.

#### 🔄 Fluxo orquestrado:
1. `orquestrador_ingestao_data_bronze`:
   - Extrai os dados da API Ploomes.
   - Salva em arquivos `.parquet` temporários.
   - Carrega os dados extraídos para o schema `bronze` do banco `cmsolar`.

2. `orquestrador_ingestao_data_prata`:
   - Extrai os dados do banco `bronze` e salva como `.parquet`.
   - Realiza as transformações necessárias (ETL).
   - Insere os dados transformados no schema `prata`.

#### 📌 Ordem garantida:
- A DAG `orquestrador_ingestao_data_bronze` deve finalizar completamente antes que a DAG `orquestrador_ingestao_data_prata` comece.
- Essa sequência é controlada com `TriggerDagRunOperator` usando `wait_for_completion=True`.

#### 🎯 Objetivo:
- Automatizar o pipeline de ponta a ponta: **da API até o schema final transformado no banco de dados**.
- Garantir consistência e rastreabilidade em todo o fluxo de ingestão e transformação de dados.




    """
) as dag:

    executar_bronze = TriggerDagRunOperator(
        task_id="executar_orquestrador_ingestao_data_bronze",
        trigger_dag_id="orquestrador_ingestao_data_bronze",
        wait_for_completion=True
    )

    executar_prata = TriggerDagRunOperator(
        task_id="executar_orquestrador_etl_completo_prata",
        trigger_dag_id="orquestrador_ingestao_data_prata",
        wait_for_completion=True
    )

    executar_bronze >> executar_prata
