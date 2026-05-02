"""
Script de teste — rode antes de qualquer pipeline para ver
exatamente o que a OpenWeather está retornando.

Como rodar:
    python test_api.py

O que ele faz:
    1. Busca tempo atual de São Paulo
    2. Busca previsão 5 dias de São Paulo
    3. Busca qualidade do ar de São Paulo
    4. Imprime o JSON completo de cada endpoint
"""

import requests
import json
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path("config") / ".env")

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.openweathermap.org"

CIDADE = "São Paulo"
PAIS   = "BR"

# Coordenadas de SP (necessárias para o endpoint de poluição)
LAT = -23.5505
LON = -46.6333


def separador(titulo: str):
    print("\n" + "=" * 60)
    print(f"  {titulo}")
    print("=" * 60)


def testar_endpoint(nome: str, url: str, params: dict):
    separador(nome)
    print(f"URL: {url}")
    print(f"Params: {params}\n")

    response = requests.get(url, params=params)

    print(f"Status code: {response.status_code}")

    if response.status_code != 200:
        print(f"ERRO: {response.text}")
        return None

    data = response.json()
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return data


if __name__ == "__main__":

    # 1. Tempo atual
    testar_endpoint(
        nome="1. TEMPO ATUAL (current weather)",
        url=f"{BASE_URL}/data/2.5/weather",
        params={
            "q": f"{CIDADE},{PAIS}",
            "units": "metric",
            "lang": "pt_br",
            "appid": API_KEY,
        }
    )

    # 2. Previsão 5 dias / 3h
    testar_endpoint(
        nome="2. PREVISÃO 5 DIAS (forecast)",
        url=f"{BASE_URL}/data/2.5/forecast",
        params={
            "q": f"{CIDADE},{PAIS}",
            "units": "metric",
            "lang": "pt_br",
            "appid": API_KEY,
        }
    )

    # 3. Qualidade do ar
    testar_endpoint(
        nome="3. QUALIDADE DO AR (air pollution)",
        url=f"{BASE_URL}/data/2.5/air_pollution",
        params={
            "lat": LAT,
            "lon": LON,
            "appid": API_KEY,
        }
    )

    print("\n" + "=" * 60)
    print("  Teste concluído!")
    print("  Analise os campos acima para entender o que cada")
    print("  endpoint retorna antes de escrever os pipelines.")
    print("=" * 60 + "\n")