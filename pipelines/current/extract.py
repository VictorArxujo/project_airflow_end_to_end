import requests
import logging
from datetime import datetime, timezone

from core.settings import settings
from core.lake import save_raw

logger = logging.getLogger(__name__)


def extract_current(city: str) -> str:
    """
    Busca o tempo atual e salva o JSON bruto no data lake.

    Retorna:
        collected_at como string ISO — XCom só serializa tipos simples (str, int, list, dict)
    """
    logger.info(f"[current/extract] Iniciando para: {city}")

    response = requests.get(
        url=f"{settings.openweather_base_url}/data/2.5/weather",
        params={
            "q": f"{city},BR",
            "units": "metric",
            "lang": "pt_br",
            "appid": settings.api_key,
        },
        timeout=10,
    )
    response.raise_for_status()

    data = response.json()
    collected_at = datetime.now(timezone.utc)

    save_raw(domain="current", city=city, data=data, collected_at=collected_at)

    # Retorna STRING — único formato seguro para o XCom do Airflow
    collected_at_str = collected_at.isoformat()
    logger.info(f"[current/extract] Concluído para {city} às {collected_at_str}")
    return collected_at_str