from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
import pandas as pd
import os
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'vanderson',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}

def extrair_tabela_para_parquet(tabela_nome: str, caminho_destino: str):
    hook = PostgresHook(postgres_conn_id='cmsolarpostgres')
    sql = f"SELECT * FROM {tabela_nome};"
    df = hook.get_pandas_df(sql)

    os.makedirs(os.path.dirname(caminho_destino), exist_ok=True)
    df.to_parquet(caminho_destino, index=False)

    print(f"Tabela {tabela_nome} salva em {caminho_destino}.")
    print(df.head(1))

with DAG(
        default_args=default_args,
        dag_id='get_data_db_to_parquet_file',
        description='Extracting data from DB bronze to parquet temporary file',
        start_date=datetime(2025, 4, 28, 1),
        schedule_interval=None,
        catchup=False,
	doc_md = 
	"""
		Esta DAG é responsável por **extrair dados diretamente do banco de dados PostgreSQL (`cmsolar`) no schema `bronze`** e salvá-los como arquivos `.parquet`.

	#### 📤 O que ela faz:
	- Conecta-se ao banco `cmsolar`, schema `bronze`.
	- Lê todas as tabelas de interesse.
	- Exporta o conteúdo para arquivos `.parquet`.
	- Salva os arquivos  na pasta tmp_parquets/bronze_parquets
	#### 🎯 Finalidade:
	- Os arquivos `.parquet` extraídos servem como base para a camada **silver**, onde ocorrerão transformações.
	- Essa DAG prepara os dados em formato leve e eficiente para leitura e processamento em etapas seguintes.

	#### 🔗 Orquestração:
	- É executada **automaticamente pela DAG `orquestrador_ingestao_data_prata`**, como parte do pipeline de preparação da camada prata.


	"""
) as dag:

    task1 = PythonOperator(
        task_id='extract_users_table',
        python_callable=extrair_tabela_para_parquet,
        retries=3,
        op_kwargs={
            'tabela_nome': 'bronze.dados_users_ploomes',
            'caminho_destino': '/opt/airflow/dags/tmp_parquets/bronze_parquets/dados_users_ploomes.parquet'
        },
        retry_delay=timedelta(minutes=2)
    )

    task2 = PythonOperator(
        task_id='extract_contacts_table',
        python_callable=extrair_tabela_para_parquet,
        retries=3,
        op_kwargs={
            'tabela_nome': 'bronze.dados_contacts_ploomes',
            'caminho_destino': '/opt/airflow/dags/tmp_parquets/bronze_parquets/dados_contacts_ploomes.parquet'
        }
    )

    task3 = PythonOperator(
        task_id='extract_loss_table',
        python_callable=extrair_tabela_para_parquet,
        op_kwargs={
            'tabela_nome': 'bronze.dados_loss_reasons_ploomes',
            'caminho_destino': '/opt/airflow/dags/tmp_parquets/bronze_parquets/dados_loss_reasons_ploomes.parquet'
        }
    )

    task4 = PythonOperator(
        task_id='extract_origins_table',
        python_callable=extrair_tabela_para_parquet,
        op_kwargs={
            'tabela_nome': 'bronze.dados_origins_ploomes',
            'caminho_destino': '/opt/airflow/dags/tmp_parquets/bronze_parquets/dados_origins_ploomes.parquet'
        }
    )

    task5 = PythonOperator(
        task_id='extract_pipeline_table',
        python_callable=extrair_tabela_para_parquet,
        op_kwargs={
            'tabela_nome': 'bronze.dados_pipelines_ploomes',
            'caminho_destino': '/opt/airflow/dags/tmp_parquets/bronze_parquets/dados_pipelines_ploomes.parquet'
        }
    )

    task6 = PythonOperator(
        task_id='extract_deals_table',
        python_callable=extrair_tabela_para_parquet,
        op_kwargs={
            'tabela_nome': 'bronze.dados_deals_ploomes',
            'caminho_destino': '/opt/airflow/dags/tmp_parquets/bronze_parquets/dados_deals_ploomes.parquet'
        }
    )

    task7 = PythonOperator(
        task_id='extract_stages_table',
        python_callable=extrair_tabela_para_parquet,
        op_kwargs={
            'tabela_nome': 'bronze.dados_stages_ploomes',
            'caminho_destino': '/opt/airflow/dags/tmp_parquets/bronze_parquets/dados_stages_ploomes.parquet'
        }
    )

    task8 = PythonOperator(
        task_id='extract_status_table',
        python_callable=extrair_tabela_para_parquet,
        op_kwargs={
            'tabela_nome': 'bronze.dados_status_deals_ploomes',
            'caminho_destino': '/opt/airflow/dags/tmp_parquets/bronze_parquets/dados_status_deals_ploomes.parquet'
        }
    )

    # Definindo a ordem de execução
    task1 >> task2 >> task3 >> task4 >> task5 >> task6 >> task7 >> task8
