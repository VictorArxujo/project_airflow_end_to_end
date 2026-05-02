from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import logging

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


def get_engine():
    from core.settings import settings
    logger.info(f"Conectando ao banco: {settings.db_host}:{settings.db_port}/{settings.db_name}")
    return create_engine(
        settings.database_url,
        pool_pre_ping=True,   # verifica conexão antes de usar
        pool_size=5,
        max_overflow=10,
    )


def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def create_all_tables():
    """Cria todas as tabelas mapeadas nos models (roda no init do container)."""
    from core import models  # noqa: F401 — importa para registrar os models no Base
    engine = get_engine()
    Base.metadata.create_all(engine)
    logger.info("Tabelas criadas/verificadas com sucesso.")