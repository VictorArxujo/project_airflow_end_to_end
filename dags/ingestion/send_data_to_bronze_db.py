from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
import os
import pandas as pd
import logging
from sqlalchemy import text

# Configurações fixas
INPUT_PATH = "/tmp"
DB_SCHEMA = "bronze"

logger = logging.getLogger("airflow.task")

# Função de adição da chave primária
def adicionar_chave_primaria(df, engine, nome_tabela):
    with engine.begin() as conn:
        # Verifica se a tabela já tem chave primária
        pk_check = conn.execute(text("""
            SELECT COUNT(*) FROM information_schema.table_constraints
            WHERE table_schema = :schema AND table_name = :table
            AND constraint_type = 'PRIMARY KEY'
        """), {"schema": DB_SCHEMA, "table": nome_tabela}).scalar()

        # Se não houver PK, tenta adicioná-la na coluna 'Id'
        if pk_check == 0 and "Id" in df.columns:
            try:
                conn.execute(text(f"""
                    ALTER TABLE {DB_SCHEMA}.\"{nome_tabela}\"
                    ADD PRIMARY KEY ("Id")
                """))
                logger.info(f"🔐 Chave primária adicionada na tabela {nome_tabela}.")
            except Exception as pk_error:
                logger.warning(f"⚠️ Falha ao adicionar chave primária em {nome_tabela}: {pk_error}")

# Função de inserção dos parquets Silver no banco
def inserir_incremental_parquets():
    hook = PostgresHook(postgres_conn_id='cmsolarpostgres')
    engine = hook.get_sqlalchemy_engine()

    arquivos = [f for f in os.listdir(INPUT_PATH) if f.endswith(".parquet")]

    if not arquivos:
        logger.warning("⚠️ Nenhum arquivo .parquet encontrado para processar.")
        return

    # Cria o schema se ainda não existir
    with engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {DB_SCHEMA}"))

    for arquivo in arquivos:
        caminho = os.path.join(INPUT_PATH, arquivo)
        nome_tabela = arquivo.replace(".parquet", "")

        try:
            df = pd.read_parquet(caminho)

            # Insere os dados na tabela, substituindo a tabela existente
            df.to_sql(
                nome_tabela,
                con=engine,
                schema=DB_SCHEMA,
                if_exists='replace',  # Garante que a tabela será recriada
                index=False
            )
            logger.info(f"✅ Tabela {nome_tabela} foi recriada com {len(df)} registros.")

            # Adiciona a chave primária caso não exista
            adicionar_chave_primaria(df, engine, nome_tabela)

        except Exception as e:
            logger.error(f"❌ Erro ao processar {arquivo}: {e}")

# Construção da DAG
def build_dag():
    default_args = {
        'owner': 'vanderson',
        'retries': 3,
        'retry_delay': timedelta(minutes=5),
        'start_date': datetime(2025, 4, 23, 2),
    }

    with DAG(
        dag_id='post_data_to_bronze_db',
        default_args=default_args,
        schedule_interval=None,
        catchup=False,
        tags=['bronze', 'load-to-db', 'carregando-dados-pro-banco'],
        doc_md="""
        ### DAG: send_data_to_bronze_db

        Esta DAG é responsável por **carregar no banco de dados PostgreSQL (`cmsolar`) os dados extraídos da API Ploomes**, que foram previamente salvos como arquivos Parquet pela DAG `get_data_from_api_ploomes`.

        #### 📥 Funcionalidade:
        - Lê todos os arquivos `.parquet` localizados na pasta temporária.
        - Cria as tabelas no schema `bronze`, caso ainda não existam.
        - Substitui a tabela inteira com os dados mais recentes.
        - Garante que a coluna `Id` seja chave primária para suportar OCDC e replicação lógica.

        #### 🔗 Dependência:
        - Executar após a DAG `get_data_from_api_ploomes`.
        - Orquestrada pela DAG `ORQUESTRADOR_INGESTAO_DATA_BRONZE`."""
    ) as dag:

        carregar_incremental = PythonOperator(
            task_id='carregar_incremental_parquets_para_postgres',
            python_callable=inserir_incremental_parquets
        )

        return dag

# Registra a DAG no Airflow
globals()['post_data_to_bronze_db'] = build_dag()
