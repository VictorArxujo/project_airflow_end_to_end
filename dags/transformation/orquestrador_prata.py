from airflow import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime, timedelta


default_args= {
	'owner': 'vanderson',
	'retries':5,
	'retry_delay': timedelta(minutes=5)



}

with DAG( 
    default_args=default_args,
    dag_id="orquestrador_ingestao_data_prata",
    start_date=datetime(2025, 4, 30),
    schedule_interval=None,
    catchup=False,
    tags=["etl", "prata"],
    description="Orquestra extração do banco + ETL para camada prata",
    doc_md=
    """
### DAG: orquestrador_ingestao_data_prata

Esta DAG atua como **orquestradora do pipeline da camada prata**, controlando a execução de duas etapas principais:

1. `get_data_db_to_parquet_file` → extrai os dados do banco de dados (schema `bronze`) e salva como arquivos `.parquet`.
2. `post_data_prata_db_and_etl` → aplica transformações nos arquivos `.parquet` (clientes e negócios) e insere os dados no schema `prata` do banco de dados `cmsolar`.

#### 🔄 Fluxo orquestrado:
orquestrador_ingestao_data_prata
├──> get_data_db_to_parquet_file
└──> post_data_prata_db_and_etl

#### ⚙️ Operadores utilizados:
- `TriggerDagRunOperator` com `wait_for_completion=True` garante que cada DAG anterior finalize antes da próxima iniciar.

#### 🧠 Objetivo:
- Centralizar a orquestração da ingestão de dados da camada prata.
- Garantir que a extração dos dados brutos do banco ocorra **antes** do processo de transformação e carga no destino final (`prata`).


    """


) as dag:

    extrair_dados_para_parquet = TriggerDagRunOperator(
        task_id="executar_get_data_db_to_parquet_file",
        trigger_dag_id="get_data_db_to_parquet_file",
        wait_for_completion=True
    )

    transformar_e_inserir_no_prata = TriggerDagRunOperator(
        task_id="executar_post_data_prata_db_and_etl",
        trigger_dag_id="post_data_prata_db_and_etl",
        wait_for_completion=True
    )

    extrair_dados_para_parquet >> transformar_e_inserir_no_prata

