import pandas as pd
import logging
from sqlalchemy.dialects.postgresql import insert

from core.db import get_engine

logger = logging.getLogger(__name__)


def load_current(df: pd.DataFrame) -> int:
    """
    Insere o DataFrame transformado na tabela weather_current do PostgreSQL.
    Ignora registros duplicados (mesmo city_name + collected_at).

    Args:
        df: DataFrame vindo do transform_current

    Returns:
        quantidade de linhas inseridas
    """
    if df.empty:
        logger.warning("[current/load] DataFrame vazio, nada para inserir.")
        return 0

    engine = get_engine()

    # converte o DataFrame para lista de dicts para usar o insert do SQLAlchemy
    records = df.to_dict(orient="records")

    with engine.begin() as conn:
        stmt = insert("weather_current").values(records)

        # on_conflict_do_nothing: se já existe city_name + collected_at iguais,
        # simplesmente ignora — não lança erro, não duplica
        stmt = stmt.on_conflict_do_nothing(
            constraint="uq_current_city_time"
        )

        result = conn.execute(stmt)
        inserted = result.rowcount

    logger.info(f"[current/load] {inserted} linha(s) inserida(s) na weather_current")
    return inserted