from pathlib import Path
import os
import re
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from airflow.providers.postgres.hooks.postgres import PostgresHook
import pandas as pd
import logging
from airflow.decorators import task
from sqlalchemy import text
from typing import Optional
logger = logging.getLogger("airflow.task")

# Configurações padrão da DAG
default_args = {
    'owner': 'vanderson',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}
def first10_to_br_date(series: pd.Series,
                       *,
                       logger=None,
                       df_name="",
                       col_name=""):
    """
    Extrai os 10 primeiros caracteres (YYYY-MM-DD), converte para datetime,
    e retorna como datetime (não string).
    """
    ymd = series.astype(str).str.slice(0, 10)
    datetimes = pd.to_datetime(ymd, format="%Y-%m-%d", errors="coerce")

    bad_mask = datetimes.isna() & series.notna()
    if bad_mask.any():
        msg = (
            f"⚠️ {bad_mask.sum()} falhas ao converter '{col_name}' "
            f"em {df_name}:\n{series[bad_mask].to_string()}"
        )
        (logger.warning if logger else print)(msg)

    return datetimes  # <- datetime, não string
def calcular_dias_para_venda(df, col_criacao='DataCriacao', col_venda='DataVenda', nova_coluna='DuracaoVenda'):
    """
    Calcula a diferença de dias entre col_criacao e col_venda.
    Assume que ambas as colunas já estão em datetime.
    """
    df[nova_coluna] = (df[col_venda] - df[col_criacao]).dt.days
    df[nova_coluna] = df[nova_coluna].apply(lambda x: max(x, 0) if pd.notnull(x) else x)
    return df

def formatar_valor_brasileiro(valor):
    valor_str = f"{valor:,.2f}"  # exemplo: '17,166.68'
    return valor_str.replace(",", "X").replace(".", ",").replace("X", ".")


# Função de transformação dos dados de deals com origens
def transformar_deals_com_origens(caminho_users: str, caminho_loss_reasons: str, caminho_deals: str,
                                  caminho_origens: str, caminho_funil: str, caminho_estagio: str, caminho_status: str):
    df_funil = pd.read_parquet(caminho_funil)
    df_users = pd.read_parquet(caminho_users)
    df_estagio = pd.read_parquet(caminho_estagio)
    df_deals = pd.read_parquet(caminho_deals)
    df_status = pd.read_parquet(caminho_status)
    df_loss_reasons = pd.read_parquet(caminho_loss_reasons)
    df_origens = pd.read_parquet(caminho_origens)[['Id', 'Name']]
    df_origens = df_origens.rename(columns={'Id': 'IdOrigem'})
    df_deals = df_deals.rename(columns={'Id': 'IdDeal'})

    df_merge = pd.merge(
        df_deals,
        df_origens,
        how='left',
        left_on='OriginId',
        right_on='IdOrigem'
    )

    df_deals = df_merge.rename(columns={'Name': 'Origem', 'Title': 'Titulo', 'ContactName': 'Cliente',
                                        'Amount': 'Valor', 'CreateDate': 'DataCriacao','FinishDate':'DataVenda','DaysInStage' : 'DiasEmEstagio'})
    




    df_deals['Origem'] = df_deals['Origem'].fillna('Origem Desconhecida')

    df_merge_funil = pd.merge(
        df_funil,
        df_estagio,
        how='left',
        left_on='Id',
        right_on='PipelineId'
    )

    df_status = df_status.rename(columns={'Id': 'IdStatus', 'Name': 'Situação'})
    df_merge_status = pd.merge(
        df_deals,
        df_status,
        left_on="StatusId",
        right_on='IdStatus',
        how='left'
    )

    df_loss_reasons = df_loss_reasons.rename(columns={'Id': 'IdLossReason', 'Name': 'Motivo da Perda'})
    df_finalty = pd.merge(
        df_merge_status,
        df_loss_reasons,
        right_on='IdLossReason',
        left_on='LossReasonId',
        how='left'
    )

    df_pipes_merge = df_merge_funil[['Name_y', 'Name_x', 'Id_x', 'Id_y']]
    df_pipes_merge = df_pipes_merge.rename(columns={'Name_x': 'Funil', 'Name_y': 'Estágio', 'Id_x': 'IdFunil', 'Id_y': 'IdEstagio'})

    df_finalv1 = pd.merge(
        df_pipes_merge,
        df_finalty,
        right_on='StageId',
        left_on='IdEstagio',
        how='inner'
    )

    df_users = df_users[['Id', 'Name']].rename(columns={'Name': 'Responsavel'})
    print(f"colunas do df{df_finalv1.columns}")
    df_finalv1 = df_finalv1[['IdDeal','Cliente', 'Estágio', 'Funil', 'Titulo', 'OwnerId', 'Valor', 'DataCriacao', 'Origem', 'Situação','DataVenda','DiasEmEstagio','Motivo da Perda']]
    df_final = pd.merge(
        df_finalv1,
        df_users,
        how='left',
        right_on='Id',
        left_on='OwnerId'
    )
    
    df_final['ValorNegocio'] = df_final['Valor'].apply(formatar_valor_brasileiro)
    print(df_final.info())
    df_final = df_final.drop(columns=['Id', 'OwnerId','Valor'])
    df_final=df_final.rename(columns={'IdDeal':'Id'})
 # ─── Conversão de datas para datetime64 com log de falhas ────────────────
    for col in ("DataCriacao", "DataVenda"):
        df_final[col] = first10_to_br_date(
            df_final[col],
            logger=logger,
            df_name="df_final",
            col_name=col
        )

    # ─── Cálculo da diferença de dias ───────────────────────────────────────
    df_final = calcular_dias_para_venda(
        df_final,
        col_criacao='DataCriacao',
        col_venda='DataVenda'
    )
    
    caminho_limpo = '/opt/airflow/dags/tmp_parquets/silver_parquets/deals_com_origens.parquet'
    os.makedirs(os.path.dirname(caminho_limpo), exist_ok=True)
    df_final.to_parquet(caminho_limpo, index=False)

    if os.path.exists(caminho_limpo):
        print(f"✅ Parquet salvo com sucesso: {caminho_limpo}")
    else:
        print(f"❌ Erro: Parquet NÃO encontrado em {caminho_limpo}")


# Função de transformação dos dados de contatos com origens
def ler_parquet_tmp(caminho_entrada_contacts: str, caminho_entrada_origins: str):
    df_contacts = pd.read_parquet(caminho_entrada_contacts)
    df_origins = pd.read_parquet(caminho_entrada_origins)[['Id', 'Name']]

    df_merge = pd.merge(df_contacts, df_origins, right_on='Id', left_on='OriginId', how='left')

    df_merge = df_merge.rename(columns={
        "Id_x": "Id",
        "Name_y": "Origem",
        "Name_x": "Cliente",
        "CreateDate": "DataCriacao"
    })

    df_contacts_final = df_merge[['Id', 'Origem', 'DataCriacao', 'Cliente', 'LastUpdateDate']]
    ## Atribuindo origem desconhecida pra quem e NaN
    df_contacts_final['Origem']=df_contacts_final['Origem'].fillna('Origem Desconhecida')
    
    print(df_contacts_final.info())
    df_contacts_final["DataCriacao"] = first10_to_br_date(
    df_contacts_final["DataCriacao"],
    logger=logger,
    df_name="df_contacts_final", 
    col_name="DataCriacao"
    )
    print(df_contacts_final.info())
    caminho_limpo = '/opt/airflow/dags/tmp_parquets/silver_parquets/dados_contacts_ploomes.parquet'
    os.makedirs(os.path.dirname(caminho_limpo), exist_ok=True)
    df_contacts_final.to_parquet(caminho_limpo, index=False)

    if os.path.exists(caminho_limpo):
        print(f"✅ Parquet salvo com sucesso: {caminho_limpo}")
    else:
        print(f"❌ Erro: Parquet NÃO encontrado em {caminho_limpo}")


# Nova versão da função de inserção no banco (sem controle de update
@task()
def inserir_incremental_silver():
    hook   = PostgresHook(postgres_conn_id="cmsolarpostgres")
    engine = hook.get_sqlalchemy_engine()

    DB_SCHEMA_SILVER   = "prata"
    INPUT_PATH_SILVER  = "/opt/airflow/dags/tmp_parquets/silver_parquets"

    with engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {DB_SCHEMA_SILVER}"))

    for file in Path(INPUT_PATH_SILVER).glob("*.parquet"):
        table_name = file.stem
        df         = pd.read_parquet(file)

        if df.empty:
            logger.info(f"⚠️ {table_name}: DataFrame vazio, nada a fazer.")
            continue

        if "Id" in df.columns:
            df = df.drop_duplicates(subset="Id")

        # Verifica se a tabela já existe
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT to_regclass(:full_table_name)
            """), {"full_table_name": f"{DB_SCHEMA_SILVER}.{table_name}"})
            table_exists = result.scalar() is not None

        # Se não existir, cria e insere os dados
        if not table_exists:
            df.to_sql(
                table_name,
                con=engine,
                schema=DB_SCHEMA_SILVER,
                if_exists="fail",
                index=False,
            )
            logger.info(f"🆕 Tabela {DB_SCHEMA_SILVER}.{table_name} criada no banco.")
        else:
            with engine.begin() as conn:
                # Garante PK + replica identity
                conn.execute(text(f"""
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.table_constraints
                            WHERE table_schema = :schema
                              AND table_name   = :table
                              AND constraint_type = 'PRIMARY KEY'
                        ) THEN
                            EXECUTE format(
                              'ALTER TABLE %I.%I ADD PRIMARY KEY ("Id")',
                              :schema, :table
                            );
                            EXECUTE format(
                              'ALTER TABLE %I.%I REPLICA IDENTITY DEFAULT',
                              :schema, :table
                            );
                        END IF;
                    END$$;
                """), {"schema": DB_SCHEMA_SILVER, "table": table_name})

                # Limpa dados e insere novos
                conn.execute(text(f'TRUNCATE {DB_SCHEMA_SILVER}."{table_name}"'))

            df.to_sql(
                table_name,
                con=engine,
                schema=DB_SCHEMA_SILVER,
                if_exists="append",
                index=False,
            )
            logger.info(f"🔄 Tabela {DB_SCHEMA_SILVER}.{table_name} atualizada com {len(df)} registros.")
# Construção da DAG
definir_dag = DAG(
    default_args=default_args,
    dag_id='post_data_prata_db_and_etl',
    start_date=datetime(2025, 4, 28, 0),
    schedule_interval=None,  # Mude para '@daily' se quiser agendamento automático
    catchup=False,
    doc_md= """	
Esta DAG é responsável por **realizar a transformação dos dados da camada bronze para a camada prata**, com foco nas tabelas de **clientes (contatos)** e **negócios (deals)**.
#### 📚 O que ela faz:
- Lê os arquivos `.parquet` localizados em `dags/tmp_parquets/bronze_parquets`
- Executa diversas transformações nas tabelas:
- `merge` entre entidades relacionadas (ex: deals com usuários, origens, estágios).
- `fillna` para preenchimento de dados nulos.
- `rename` e reestruturação de colunas.
- Seleção e reorganização de dados relevantes para análise.

#### 🧾 Comportamento de carga:
- Os dados transformados são inseridos no **schema `prata`** do banco de dados `cmsolar`.
- **Não realiza updates parciais**: toda execução remove os registros existentes nas tabelas de destino e insere todos os dados novamente (**delete + insert**).

#### 🔗 Orquestração:
- Esta DAG é executada como parte do pipeline de ingestão da camada prata, sendo **acionada pela DAG `orquestrador_ingestao_data_prata`**.
        """
)

with definir_dag as dag:
    clean_transform = PythonOperator(
        task_id='transforming_contacts_etl',
        python_callable=ler_parquet_tmp,
        op_kwargs={
            'caminho_entrada_origins': '/opt/airflow/dags/tmp_parquets/bronze_parquets/dados_origins_ploomes.parquet',
            'caminho_entrada_contacts': '/opt/airflow/dags/tmp_parquets/bronze_parquets/dados_contacts_ploomes.parquet'
        },
        execution_timeout=timedelta(minutes=10),
	
    )

    cleans_transform_deals = PythonOperator(
        task_id='transforming_deals_etl',
        python_callable=transformar_deals_com_origens,
        op_kwargs={
            'caminho_users': '/opt/airflow/dags/tmp_parquets/bronze_parquets/dados_users_ploomes.parquet',
            'caminho_loss_reasons': '/opt/airflow/dags/tmp_parquets/bronze_parquets/dados_loss_reasons_ploomes.parquet',
            'caminho_deals': '/opt/airflow/dags/tmp_parquets/bronze_parquets/dados_deals_ploomes.parquet',
            'caminho_origens': '/opt/airflow/dags/tmp_parquets/bronze_parquets/dados_origins_ploomes.parquet',
            'caminho_funil': '/opt/airflow/dags/tmp_parquets/bronze_parquets/dados_pipelines_ploomes.parquet',
            'caminho_estagio': '/opt/airflow/dags/tmp_parquets/bronze_parquets/dados_stages_ploomes.parquet',
            'caminho_status': '/opt/airflow/dags/tmp_parquets/bronze_parquets/dados_status_deals_ploomes.parquet'
        },
        execution_timeout=timedelta(minutes=10)
    )

    inserir_incremental_silver_task = inserir_incremental_silver()

    clean_transform >> cleans_transform_deals >> inserir_incremental_silver_task
