from services.tempok_service import TempokService
from services.intelup_service import enviar_tags
from utils.tratamento import transformar_para_intelup, interpolar_pchip, multiobserved_para_dataframe, interpolar_pchip_simples
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from datetime import datetime, timedelta
import pandas as pd
import time
from loggs import logging

VARIAVEIS_MULTIOBS = ["ghi", "gpoa", "temp_cell", "precipitation", "air_temperature"]

def log_retry(retry_state):
    logging.warning(
        f"Tentativa {retry_state.attempt_number} falhou — "
        f"Aguardando 5s antes de tentar novamente... "
        f"Erro: {retry_state.outcome.exception()}"
    )

api_retry = retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(5),
    retry=retry_if_exception_type((ConnectionError, TimeoutError, Exception)),
    before_sleep=log_retry,
    reraise=True
)

@api_retry
def executar_backfill(tempok: TempokService):
    dia_backfill = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')

    print(f"\n=== BACKFILL iniciando para {dia_backfill} ===")
    logging.info(f"Backfill iniciado para {dia_backfill}")

    plantas = tempok.plants()["plants"]
    plant_ids = [p["id"] for p in plantas]

    dados_brutos = tempok.multiobserved_intervalo(
        plant_id=plant_ids,
        variables=VARIAVEIS_MULTIOBS,
        date=dia_backfill
    )

    df = multiobserved_para_dataframe(dados_brutos, freq='1h')

    colunas_irradiancia = [c for c in df.columns if c[1] in {"ghi", "gpoa"}]
    colunas_simples     = [c for c in df.columns if c[1] in {"temp_cell", "air_temperature", "precipitation"}]

    df_irrad  = interpolar_pchip(df[colunas_irradiancia], freq_saida='5min')
    df_simple = interpolar_pchip_simples(df[colunas_simples], freq_saida='5min')

    df_interp = pd.concat([df_irrad, df_simple], axis=1)
    payload   = transformar_para_intelup(df_interp, plantas)

    for unit_code, lista_dados in payload.items():
        time.sleep(2)
        resultado = enviar_tags(unit_code, lista_dados)
        print(f"Backfill enviado ({unit_code}): {resultado}")
        logging.info(f"Backfill enviado para unit_code={unit_code}")

    print("=== BACKFILL concluído ===")


if __name__ == "__main__":
    tempok = TempokService()

    try:
        executar_backfill(tempok)
    except KeyboardInterrupt:
        logging.warning("Coletor parado manualmente.")
    except Exception as e:
        logging.error(f"Erro crítico: {e}")
        raise