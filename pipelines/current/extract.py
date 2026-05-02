import requests
import logging
from datetime import datetime, timezone

from core.settings import settings
from core.lake import save_raw

logger = logging.getLogger(__name__)


def extract_current(city: str) -> datetime:
    """
    Busca o tempo atual de uma cidade na OpenWeather e salva
    o JSON bruto no data lake local.

    Args:
        city: nome da cidade (ex: "Londrina")

    Returns:
        collected_at: datetime da coleta — passado para o transform saber
                      qual arquivo carregar
    """
    logger.info(f"[current/extract] Iniciando extração para: {city}")

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

    response.raise_for_status()  # lança exceção se status != 200

    data = response.json()
    collected_at = datetime.now(timezone.utc)

    save_raw(domain="current", city=city, data=data, collected_at=collected_at)

    logger.info(f"[current/extract] Concluído para {city} às {collected_at}")
    return collected_at