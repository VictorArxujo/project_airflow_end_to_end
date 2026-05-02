from datetime import datetime, timezone, timedelta
from utils.infos import MAPA_USINAS
from loggs import logging
import pandas as pd
import numpy as np
from scipy.interpolate import PchipInterpolator

FUSO_BRASILIA = timezone(timedelta(hours=-3))
VARIAVEIS_INTERPOLACAO_SIMPLES = {"temp_cell", "air_temperature", "precipitation"}


def _utc_para_brasilia(timestamp_utc: str) -> str:
    dt_utc = datetime.fromisoformat(timestamp_utc).replace(tzinfo=timezone.utc)
    dt_brasilia = dt_utc.astimezone(FUSO_BRASILIA)
    return dt_brasilia.strftime('%Y-%m-%dT%H:%M:%S')

def api_to_dataframe(dados_tempok: dict, freq: str = '10min') -> pd.DataFrame:
    times = dados_tempok.get("times", [])
    dados = dados_tempok.get("data", [])

    if not times or not dados:
        logging.error("Payload vazio ou malformado.")
        return pd.DataFrame()

    frames = {}
    for planta in dados:
        nome   = planta["id"]
        values = planta.get("values", {})

        df_planta = pd.DataFrame(values, index=pd.to_datetime(times))
        df_planta = df_planta.apply(pd.to_numeric, errors='coerce').fillna(0)
        df_planta = df_planta.clip(lower=0)  # <- qualquer valor negativo (ex: -999) vira 0

        frames[nome] = df_planta

    df = pd.concat(frames, axis=1)
    df.index.name = "time"
    df = df.asfreq(freq)

    return df

def interpolar_pchip(df_input: pd.DataFrame, freq_saida: str = '5min') -> pd.DataFrame:
    freq_entrada_min = int(pd.tseries.frequencies.to_offset(df_input.index.freq).nanos / 1e9 / 60)
    freq_saida_min   = int(pd.tseries.frequencies.to_offset(freq_saida).nanos / 1e9 / 60)
    limit_janelas    = freq_entrada_min // freq_saida_min - 1

    print(f"\nFreq entrada: {freq_entrada_min}min | Freq saída: {freq_saida_min}min | Limit: {limit_janelas} janelas")

    df_resampled = df_input.resample(freq_saida).asfreq()
    x_novo       = np.array([t.timestamp() for t in df_resampled.index])
    df_resultado = df_resampled.copy()

    for coluna in df_input.columns:
        y = df_input[coluna].values.astype(float)

        mascara_validos = y > 0
        if mascara_validos.sum() < 2:
            print(f"  [{coluna}] Pontos válidos insuficientes, pulando.")
            continue

        x_original = np.array([t.timestamp() for t in df_input.index])

        # Pega o primeiro e último índice com dado válido
        idx_primeiro = np.argmax(mascara_validos)
        idx_ultimo   = len(mascara_validos) - 1 - np.argmax(mascara_validos[::-1])

        # Adiciona ponto zero 1 hora antes do primeiro dado e 1 hora depois do último
        x_ancora_inicio = x_original[idx_primeiro] - 3600
        x_ancora_fim    = x_original[idx_ultimo]   + 3600

        x_com_ancoras = np.concatenate([[x_ancora_inicio], x_original[mascara_validos], [x_ancora_fim]])
        y_com_ancoras = np.concatenate([[0], y[mascara_validos], [0]])

        interpolador = PchipInterpolator(x_com_ancoras, y_com_ancoras, extrapolate=False)

        y_interpolado = interpolador(x_novo)

        y_interpolado = np.where(
            (y_interpolado is None) | np.isnan(y_interpolado),
            0, y_interpolado
        )
        y_interpolado = np.clip(y_interpolado, 0, None)

        df_resultado[coluna] = y_interpolado

    return df_resultado

def transformar_para_intelup(df: pd.DataFrame, plantas: list[dict]) -> dict[str, list]:
    if df.empty:
        logging.error("DataFrame vazio.")
        return {}

    nome_para_id = {p["name"]: p["id"] for p in plantas}
    resultado = {}

    for chave in df.columns.get_level_values(0).unique():
        id_num = nome_para_id.get(chave) if isinstance(chave, str) else chave

        if id_num is None:
            continue

        mapeamento_bruto = MAPA_USINAS.get(id_num)
        if not mapeamento_bruto:
            continue

        # --- NOVA LÓGICA: Transforma tudo em lista para processar igual ---
        if isinstance(mapeamento_bruto, dict):
            lista_destinos = [mapeamento_bruto]
        else:
            lista_destinos = mapeamento_bruto

        # Itera sobre cada destino (ex: vai passar por Malbec e depois por Catena)
        for destino in lista_destinos:
            unit_code = destino["unit_code"]
            tags = destino["tags"]

            if unit_code not in resultado:
                resultado[unit_code] = []

            for variavel, tag_code in tags.items():
                if (chave, variavel) not in df.columns:
                    continue

                for timestamp, valor in df[chave][variavel].items():
                    if pd.isna(valor):
                        continue
                    
                    resultado[unit_code].append({
                        "tagCode": tag_code,
                        "value":   round(float(valor), 4),
                        "time":    _utc_para_brasilia(timestamp.strftime('%Y-%m-%dT%H:%M:%S')),
                    })

    return resultado

def multiobserved_para_dataframe(dados_brutos: dict, freq: str = '1h') -> pd.DataFrame:

    dados = dados_brutos.get("data", [])

    if not dados:
        logging.error("Payload do multiobserved vazio ou malformado.")
        return pd.DataFrame()

    frames = {}
    for planta in dados:
        id_num = planta["id"]
        times  = planta.get("times", [])

        variaveis = {k: v for k, v in planta.items() if k not in ("id", "times")}

        df_planta = pd.DataFrame(variaveis, index=pd.to_datetime(times))
        df_planta = df_planta.apply(pd.to_numeric, errors='coerce')  # null vira NaN
        df_planta = df_planta.fillna(0)
        frames[id_num] = df_planta

    df = pd.concat(frames, axis=1)  # MultiIndex: (id_numerico, variavel)
    df.index.name = "time"
    df = df.asfreq(freq)

    return df

def interpolar_pchip_simples(df_input: pd.DataFrame, freq_saida: str = '5min') -> pd.DataFrame:
    """
    Interpolação PCHIP simples para variáveis que não têm comportamento de curva solar.
    Só interpola entre pontos reais observados — não extrapola, não força zero.
    """
    freq_entrada_min = int(pd.tseries.frequencies.to_offset(df_input.index.freq).nanos / 1e9 / 60)
    freq_saida_min   = int(pd.tseries.frequencies.to_offset(freq_saida).nanos / 1e9 / 60)

    print(f"\n[Simples] Freq entrada: {freq_entrada_min}min | Freq saída: {freq_saida_min}min")

    df_resampled = df_input.resample(freq_saida).asfreq()
    x_novo       = np.array([t.timestamp() for t in df_resampled.index])
    df_resultado = df_resampled.copy()

    for coluna in df_input.columns:
        y = df_input[coluna].values.astype(float)

        # Só pontos não-NaN e não-zero são válidos
        mascara_validos = ~np.isnan(y) & (y != 0)

        if mascara_validos.sum() < 2:
            print(f"  [{coluna}] Pontos válidos insuficientes, pulando.")
            continue

        x_original = np.array([t.timestamp() for t in df_input.index])
        x_interp   = x_original[mascara_validos]
        y_interp   = y[mascara_validos]

        interpolador  = PchipInterpolator(x_interp, y_interp, extrapolate=False)
        y_interpolado = interpolador(x_novo)

        # Fora do range dos dados reais fica NaN — não inventa nada
        df_resultado[coluna] = y_interpolado

    return df_resultado