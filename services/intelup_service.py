import requests
from typing import List, Dict, Any
from utils.functions import retorna_hora_atual_formatada
import dotenv
import os

dotenv.load_dotenv()

# Configurações fixas

url_portal = os.getenv('URL_PORTAL_INTELUP')
token = os.getenv('TOKEN_PORTAL_INTELUP')
code = os.getenv('CODE_INTELUP')

def enviar_tags(unit_code, dados: List[Dict[str, Any]]) -> Any:

    HEADERS = {
        "token": token,
        "code": code,
        "unit-code": unit_code, # Numero da planta
        "Content-Type": "application/json",
    }

    payload = []
    for item in dados:
        payload.append(
            {
                "tagCode": item["tagCode"],
                "value": item["value"],
                "time": item["time"],
                "status": 1,
            }
        )

    try:
        response = requests.post(url=url_portal, headers=HEADERS, json=payload)
        response.raise_for_status()
        print("Dados enviados com sucesso!")
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao enviar dados: {e}")
        return None