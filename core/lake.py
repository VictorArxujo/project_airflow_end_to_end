import json
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path

from core.settings import settings

logger = logging.getLogger(__name__)


def _build_path(domain: str, city: str, collected_at: datetime) -> Path:
    """
    Monta o caminho do arquivo raw:
    data/raw/{domain}/{city}/{YYYY-MM-DD}/{city}_{YYYYMMDD_HHMMSS}.json
    """
    city_slug = city.lower().replace(" ", "_")
    date_str  = collected_at.strftime("%Y-%m-%d")
    file_name = f"{city_slug}_{collected_at.strftime('%Y%m%d_%H%M%S')}.json"

    path = settings.raw_dir / domain / city_slug / date_str / file_name
    return path


def save_raw(domain: str, city: str, data: dict, collected_at: datetime | None = None) -> Path:
    """
    Salva o payload bruto da API como JSON no data lake local.

    Args:
        domain:       'current' | 'forecast' | 'pollution'
        city:         nome da cidade (ex: 'São Paulo')
        data:         payload bruto retornado pela API
        collected_at: datetime da coleta (default: agora em UTC)

    Returns:
        Path do arquivo salvo
    """
    if collected_at is None:
        fuso_br = timezone(timedelta(hours=-3))
        collected_at = datetime.now(fuso_br)

    path = _build_path(domain, city, collected_at)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info(f"[lake] Raw salvo: {path}")
    return path


def load_raw(domain: str, city: str, collected_at: datetime) -> dict:
    """
    Carrega um arquivo raw do data lake pelo domain + cidade + datetime exato.
    """
    path = _build_path(domain, city, collected_at)

    if not path.exists():
        raise FileNotFoundError(f"Raw não encontrado: {path}")

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    logger.info(f"[lake] Raw carregado: {path}")
    return data


def load_latest_raw(domain: str, city: str) -> dict:
    """
    Carrega o arquivo raw mais recente de um domain + cidade.
    Útil para reprocessar sem precisar saber o timestamp exato.
    """
    city_slug = city.lower().replace(" ", "_")
    base = settings.raw_dir / domain / city_slug

    if not base.exists():
        raise FileNotFoundError(f"Nenhum raw encontrado para: {domain}/{city_slug}")

    # pega todos os .json recursivamente e ordena por nome (timestamp no nome garante ordem)
    files = sorted(base.rglob("*.json"))
    if not files:
        raise FileNotFoundError(f"Pasta existe mas está vazia: {base}")

    latest = files[-1]
    with open(latest, encoding="utf-8") as f:
        data = json.load(f)

    logger.info(f"[lake] Raw mais recente carregado: {latest}")
    return data